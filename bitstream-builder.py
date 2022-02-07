# The Microchip Bitstream Builder is released under the following software licese:

#  Copyright 2021 Microchip Corporation.
#  SPDX-License-Identifier: MIT

#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.

import argparse
import io
import os
import platform
import shutil
import zipfile

import git
import requests
import yaml


# Parse command line arguments and set tool locations
def parse_args_linux():
    global libero
    global mss_configurator
    global softconsole_headless
    global programming
    global update
    global clean

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding tool path arguments
    parser.add_argument("-l", "--libero_soc_install_directory",
                        help="Install directory for Libero SoC v2021.3 to be used when running this script. For example: /usr/local/microsemi/Libero_SoC_v2021.2/")
    parser.add_argument("-s", "--softconsole_install_directory",
                        help="Install directory for SoftConsole v2021.3 to be used when running this script. For example: /home/hugh/Microchip/SoftConsole-v2021.3-7.0.0.599/")
    parser.add_argument("-L", "--lm_license_file",
                        help="LM License to be used when running Libero as part of this script. For example 1703@localhost")

    # Adding flow arguments
    parser.add_argument("-P", "--program",
                        help='Passing this argument and "True" will attempt programming of a connected target (Icicle Kit) once the bitstream has been built')
    parser.add_argument("-U", "--design_update",
                        help='Passing this argument and "True" will run the flow so that a design is generated with all of its SmartDesign, HDL and constraint components but will not generate a bitstream, generate eNVM or sNVM clients or run the Libero flow.')
    parser.add_argument("-C", "--clean",
                        help='Passing this argument and "True" will delete all sources and output files without cloning / building any sources or generating a bitstream.')

    # Read arguments from command line
    args = parser.parse_args()

    # Set up tool paths based on arguments - if not argument is passed and the tool isn't found in path / its own env variable a default path will be used to attempt to run the demo
    user_home = os.path.expanduser("~")
    if args.libero_soc_install_directory:
        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.join(
            str(args.libero_soc_install_directory) + "Libero/bin/")
        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.join(
            str(args.libero_soc_install_directory) + "Libero/bin64/")
        if os.environ.get('FPGENPROG') is None:
            os.environ["FPGENPROG"] = os.path.join(str(args.libero_soc_install_directory) + "Libero/bin64/fpgenprog")
    elif "Libero/bin/" not in os.environ["PATH"]:
        print(
            "Libero path not passed as an argument or found in the system path - attampting to use the default path for v2021.3")
        os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.3/Libero/bin/"
        os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.3/Libero/bin64/"

    if os.environ.get('FPGENPROG') is None:
        print("FPGENPROG enviroment variable is not set - attempting to use default path for v2021.3")
        os.environ["FPGENPROG"] = "/usr/local/microsemi/Libero_SoC_v2021.3/Libero/bin64/fpgenprog"

    if args.softconsole_install_directory:
        if os.environ.get('SC_INSTALL_DIR') is None:
            os.environ["SC_INSTALL_DIR"] = str(args.softconsole_install_directory)
        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.join(
            str(args.softconsole_install_directory) + "eclipse/")
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + os.path.join(str(args.softconsole_install_directory) + "python/bin")
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + os.path.join(
            str(args.softconsole_install_directory) + "riscv-unknown-elf-gcc/bin")
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + os.path.join(
            str(args.softconsole_install_directory) + "eclipse/jre/bin")
    elif "SoftConsole" not in os.environ["PATH"]:
        print(
            "SoftConsole path not passed as an argument or found in the system path - attampting to use the default path for v2021.3")
        os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/python/bin"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/riscv-unknown-elf-gcc/bin"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/jre/bin"

    if os.environ.get('SC_INSTALL_DIR') is None:
        print("SC_INSTALL_DIR enviroment variable is not set - attempting to use default path for v2021.3")
        os.environ["SC_INSTALL_DIR"] = user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599"

    if args.lm_license_file:
        os.environ[
            "LM_LICENSE_FILE"] = str(args.lm_license_file)

    # Tool call variables - these are the names of the tools to run which will be called from os.system.
    # Full paths could be used here instead of assuming tools are in PATH
    libero = "libero"
    mss_configurator = "pfsoc_mss"
    softconsole_headless = "softconsole-headless"

    # Set up the run based on flow arguments - used to indicate a design update or if programming is required
    if "true" in str(args.program).lower():
        programming = True
    else:
        programming = False

    if "true" in str(args.design_update).lower():
        update = True
    else:
        update = False

    if "true" in str(args.clean).lower():
        clean = True
    else:
        clean = False


# Checks to see if all of the required tools are installed and present in path, if a needed tool isn't available the script will exit
def check_tool_status_linux():
    if shutil.which("libero") is None:
        print("Error: libero not found in path")
        exit()

    if shutil.which("pfsoc_mss") is None:
        print("Error: polarfire soc mss configurator not found in path")
        exit()

    if shutil.which("softconsole-headless") is None:
        print("Error: softconsole headless not found in path")
        exit()

    if os.environ.get('LM_LICENSE_FILE') is None:
        print("Error: no libero license found")
        exit()

    if os.environ.get('SC_INSTALL_DIR') is None:
        print(
            "Error: SC_INSTALL_DIR enviroment variable not set, please set this variable and point it to the "
            "appropriate SoftConsole insatllation directory to run this script")
        exit()

    if os.environ.get('FPGENPROG') is None:
        print(
            "Error: FPGENPROG enviroment variable not set, please set this variable and point it to the appropriate "
            "FPGENPROG executable to run this script")
        exit()

    path = os.environ["PATH"]

    if "/python/bin" not in path:
        print(
            "The path to the SoftConsole python installation needs to be set in PATH to run this script")
        exit()

    if "/riscv-unknown-elf-gcc/bin" not in path:
        print(
            "The path to the RISC-V toolchain needs to be set in PATH to run this script")
        exit()

    if "/eclipse/jre/bin" not in path:
        print(
            "The path to the SoftConsole Java installation needs to be set in PATH to run this script")
        exit()


# Parse command line arguments and set tool locations
def parse_args_windows():
    global libero
    global mss_configurator
    global programming
    global update
    global clean

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding tool path arguments
    parser.add_argument("-l", "--libero_soc_executable",
                        help="Location of the Libero SoC v2021.3 executable to be used when running this script. For example: C:\\Microsemi\\Libero_SoC_v2021.3\\Designer\\bin\\libero.exe")
    parser.add_argument("-p", "--polarfire_soc_mss_configurator_executable",
                        help="Location of the PolarFire SoC MSS Configurator executable to be used when running this script. For example: C:\\Microsemi\\Libero_SoC_v2021.3\\Designer\\bin64\\pfsoc_mss.exe")

    # Adding flow arguments
    parser.add_argument("-P", "--program",
                        help='Passing this argument and "True" will attempt programming of a connected target (Icicle Kit) once the bitstream has been built')
    parser.add_argument("-U", "--design_update",
                        help='Passing this argument will run the flow so that a design is generated with all of its SmartDesign, HDL and constraint components but will not generate a bitstream, generate eNVM or sNVM clients or run the Libero flow.')
    parser.add_argument("-C", "--clean",
                        help='Passing this argument and "True" will delete all sources and output files without cloning / building any sources or generating a bitstream.')

    # Read arguments from command line
    args = parser.parse_args()

    # Set up tool paths based on arguments - if not argument is passed and the tool isn't found in path / its own env variable a default path will be used to attempt to run the demo
    if args.libero_soc_executable:
        libero = args.libero_soc_executable
    elif "Libero_SoC_v2021.3\\Designer\\bin\\libero.exe" not in os.environ["PATH"]:
        print(
            "Libero executable not passed as an argument or found in the system path - attampting to use the default path for v2021.3")
        libero = "C:\\Microsemi\\Libero_SoC_v2021.3\\Designer\\bin\\libero.exe"

    if args.polarfire_soc_mss_configurator_executable:
        mss_configurator = args.polarfire_soc_mss_configurator_executable
    elif "Libero_SoC_v2021.3\\Designer\\bin64\\pfsoc_mss.exe" not in os.environ["PATH"]:
        print(
            "PolarFire SoC MSS Configurator executable not passed as an argument or found in the system path - attampting to use the default path for v2021.3")
        mss_configurator = "C:\\Microsemi\\Libero_SoC_v2021.3\\Designer\\bin64\\pfsoc_mss.exe"

    # Set up the run based on flow arguments - used to indicate a design update or if programming is required
    if "true" in str(args.program).lower():
        programming = True
    else:
        programming = False

    if "true" in str(args.design_update).lower():
        update = True
    else:
        update = False

    if "true" in str(args.clean).lower():
        clean = True
    else:
        clean = False


# Checks to see if all of the required tools are installed, if a needed tool isn't available the script will exit
def check_tool_status_windows():
    if not os.path.isfile(libero):
        print("Error: libero not found")
        exit()

    if not os.path.isfile(mss_configurator):
        print("Error: polarfire soc mss configurator not found")
        exit()


# Creates required folders and removes artifacts before beginning
def init_workspace():
    # Create the sources folder to clone into if it doesn't exist (any existing source folders are handled in the
    # clone_sources function)
    if not os.path.exists("./sources"):
        os.mkdir("./sources")

    # delete the output folder if it exists to remove old artifacts
    if os.path.exists("./output"):
        shutil.rmtree('./output')

    # Create each output sub-directory
    os.mkdir("./output")
    os.mkdir("./output/MSS")
    os.mkdir("./output/HSS")
    os.mkdir("./output/bare-metal")
    os.mkdir("./output/payload")
    os.mkdir("./output/clients")
    os.mkdir("./output/final-files")


# clones the sources specified in the sources.yaml file
def clone_sources(source_list):
    source_directories = {}
    with open(source_list) as f:  # open the yaml file passed as an arg
        data = yaml.load(f, Loader=yaml.FullLoader)

        keys = data.keys()
        # each entry in the file is a source
        for source in keys:

            # Check if this is a git source
            if "git" in data.get(source).get("type"):

                # Check if we've already cloned the repo
                if os.path.exists(os.path.join("./sources", source)):
                    repo = git.Repo.init(os.path.join("./sources", source))  # set up repo
                    repo.git.checkout(data.get(source).get("branch"))  # checkout the branch from the yaml file
                    repo.remotes.origin.pull()  # pull changes

                # We don't already have the repo, clone it
                else:
                    repo = git.Repo.clone_from(data.get(source).get("link"), os.path.join("./sources", source),
                                               branch=data.get(source).get("branch"))

                # check if a specific commit from this branch is required
                if "commit" in data.get(source):
                    repo.git.checkout(data.get(source).get("commit"))  # check out a specific commit

            # Check if this is source is a url to a zip
            elif "zip" in data.get(source).get("type"):

                # if we already have a source of the same name delete it - can't check versions
                if os.path.exists(os.path.join("./sources", source)):
                    shutil.rmtree(os.path.join("./sources", source))
                r = requests.get(data.get(source).get("link"))  # download zip
                z = zipfile.ZipFile(io.BytesIO(r.content))  # extract zip
                z.extractall(os.path.join("./sources", source))  # save contents
            source_directories[source] = os.path.join("./sources",
                                                      source)  # Generate a dictionary of all of the sources that were cloned

    # return the dictionary of sources
    return source_directories


# calls the MSS configurator and generates an MSS configuration in a directory based on a cfg file
def make_mss_config(mss_configurator, config_file, output_dir):
    os.system(mss_configurator + ' -CONFIGURATION_FILE:' + config_file + ' -OUTPUT_DIR:' + output_dir)


def check_native_platform():
    if os.path.isfile('/.dockerenv'):
        return ""
    else:
        return " --native"


# Builds the HSS using a pre-defined config file using SoftConsole in headless mode
def make_hss(hss_source):
    # Update XML in HSS project
    os.remove(os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))
    shutil.copyfile("./output/MSS/test_mss_mss_cfg.xml",
                    os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))

    # Add custom build configuration
    shutil.copyfile("recipes/HSS/spi-boot-hss.config", os.path.join(hss_source, "./.config"))

    # create softconsole headless call
    workspace = " --workspace=" + os.path.join(os.getcwd(), "output", "bare-metal", "workspace")
    project = " --import=" + hss_source
    build = " --build=hart-software-services/Default"
    native = check_native_platform()
    softconsole_call = workspace + project + build + native
    os.system(softconsole_headless + softconsole_call)

    # copy the build artifact to the output directory
    shutil.copyfile("./sources/HSS/Default/bootmode1/hss-envm-wrapper-bm1-p0.hex",
                    "./output/HSS/hss-envm-wrapper-bm1-p0.hex")


# builds a bare metal project using softconsole
def make_bare_metal(softconsole_headless, bare_metal_source):
    # create a softconsole call
    workspace = " --workspace=" + os.path.join(os.getcwd(), "output", "bare-metal", "workspace")
    project = " --import=" + os.path.join(bare_metal_source, "driver-examples/mss/mss-mmuart/mpfs-mmuart-interrupt/")
    build = " --build=mpfs-mmuart-interrupt/DDR-Release"
    native = check_native_platform()
    softconsole_call = workspace + project + build + native

    # build the project
    os.system(softconsole_headless + softconsole_call)

    # copy the project artifact to the output directory
    shutil.copyfile(
        "./sources/bare-metal-examples/driver-examples/mss/mss-mmuart/mpfs-mmuart-interrupt/DDR-Release/mpfs-mmuart-interrupt.bin",
        "./output/bare-metal/mpfs-mmuart-interrupt.bin")


# Generates a HSS payload using the HSS payload generator using a config file
def make_hss_payload(payload_generator, config, destination):
    # backup current directory and change in to the payload generator directory
    top_dir = os.getcwd()
    os.chdir(payload_generator)

    # Switch here for Windows or Linux for the tool call
    if platform.system() == "Linux" or platform.system() == "Linux2":
        # make sure the tool is executable (we download and extract it as a zip source)
        os.system("chmod +x ./hss-payload-generator")

        # Generate the payload with the output going to the output directory
        os.system("./hss-payload-generator -c " + config + " " + destination)

    else:
        os.system("hss-payload-generator.exe -c " + config + " " + destination)

    # Change back to the original directory
    os.chdir(top_dir)


# Calls Libero and runs a script
def call_libero(libero, script):
    os.system(libero + " SCRIPT:" + script)


if __name__ == '__main__':
    global libero
    global mss_configurator
    global softconsole_headless
    global programming
    global update
    global clean

    # Check host system
    print("This is a " + platform.system() + " system.")

    # Set up paths for Linux and check tools are available
    if platform.system() == "Linux" or platform.system() == "Linux2":
        # The following section can be used to set up paths and environment variables used by these scripts with typical values
        # It is recommended to set these environment variables outside the script environment on the host PC
        parse_args_linux()

        # This function will check if all of the required tools are present and quit if they aren't
        check_tool_status_linux()

        # Set up paths for Windows using full paths as tool names.
    # Default installation directories used below
    elif platform.system() == "Windows":
        parse_args_windows()

        # This function will check if all of the required tools are present and quit if they aren't
        check_tool_status_windows()

    else:
        print("This does not appear to be a supported platform.")
        exit()

    if clean:
        if os.path.exists("./output"):
            shutil.rmtree('./output')
        if os.path.exists("./sources"):
            shutil.rmtree('./sources')

        exit()

    sources = {}

    # Bitstream building starts here - see individual functions for a description of their purpose
    print("Initializing workspace")
    init_workspace()

    print("Cloning sources")
    sources = clone_sources("sources.yaml")

    print("Generating MSS configuration")
    make_mss_config(mss_configurator, "./sources/HDL/MSS/vcs_mss.cfg", os.path.join(os.getcwd(), "output/MSS"))

    if not update:
        # SoftConsole headless is only available on Linux
        # Build the HSS and bare metal using SC headless when on Linux
        # The payload generator needs a different config file for windows and linux due to paths.
        if platform.system() == "Linux" or platform.system() == "Linux2":
            print("Building HSS")
            make_hss(sources["HSS"])

            print("Building bare metal")
            make_bare_metal(softconsole_headless, sources["bare-metal-examples"])

            print("Generating HSS payload")
            make_hss_payload(os.path.join(sources["HSS-payload-generator"], "hss-payload-generator/binaries/"),
                             os.path.join(os.getcwd(),
                                          "recipes/hss-payload/config_lin.yaml"),
                             os.path.join(os.getcwd(), "output/payload/spi.bin"))

        # If we're on Windows use the pre-built HSS and bare metal executables.
        # The HSS payload generator needs a windows specific config file for paths.
        else:
            print("Using pre-built HSS")
            shutil.copyfile(
                os.path.join(os.getcwd(),
                             "sources/pre-built-executables/vcs_demo_artifacts/hss-envm-wrapper-bm1-p0.hex"),
                os.path.join(os.getcwd(), "output/HSS/hss-envm-wrapper-bm1-p0.hex"))

            print("Using pre-built bare metal")
            shutil.copyfile(
                os.path.join(os.getcwd(), "sources/pre-built-executables/vcs_demo_artifacts/mpfs-mmuart-interrupt.bin"),
                os.path.join(os.getcwd(), "./output/bare-metal/mpfs-mmuart-interrupt.bin"))

            print("Generating HSS payload")
            make_hss_payload(os.path.join(sources["HSS-payload-generator"], "hss-payload-generator/binaries/"),
                             os.path.join(os.getcwd(),
                                          "recipes/hss-payload/config_win.yaml"),
                             os.path.join(os.getcwd(), "output/payload/spi.bin"))

    print("Generating Libero project")
    call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/generate-project.tcl"))

    if not update:
        print("Running the Libero flow")
        call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/run-flow.tcl"))

        print("Importing clients")
        call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/import-clients.tcl"))

        print("Exporting output files to the output/final-files directory")
        call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/export-data.tcl"))

        if programming:
            print("Programming target")
            call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/program-device.tcl"))

    else:
        print(
            "The libero project has been generated and can now be opened by opening the project file in the output/libero_project directory")

    print("Finished")
