import os
import platform
import yaml
import git
import requests
import zipfile
import io
import shutil


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


# Builds the HSS using a pre-defined config file using SoftConsole in headless mode
def make_hss(hss_source):
    # Update XML in HSS project
    os.remove(os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))
    shutil.copyfile("./output/MSS/test_mss_mss_cfg.xml",
                    os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))

    # remove buggy file in project and replace
    os.remove(os.path.join(hss_source, "include/hss_debug.h"))
    shutil.copyfile("recipes/HSS/hss_debug.h", os.path.join(hss_source, "./include/hss_debug.h"))

    # Add custom build configuration
    shutil.copyfile("recipes/HSS/spi-boot-hss.config", os.path.join(hss_source, "./.config"))

    # create softconsole headless call
    workspace = " --workspace=" + os.path.join(os.getcwd(), "output", "bare-metal", "workspace")
    project = " --import=" + hss_source
    build = " --build=hart-software-services/Default"
    native = " --native"
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
    native = " --native"
    softconsole_call = workspace + project + build + native

    # build the project
    os.system(softconsole_headless + softconsole_call)

    # copy the project artifact to the output directory
    shutil.copyfile(
        "./sources/bare-metal-examples/driver-examples/mss/mss-mmuart/mpfs-mmuart-interrupt/DDR-Release/mpfs-mmuart-interrupt.elf",
        "./output/bare-metal/mpfs-mmuart-interrupt.elf")


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

    elif platform.system() == "win32" or platform.system() == "win64" or "_NT" in platform.system() or platform.system() == "Windows":
        os.system("hss-payload-generator.exe -c " + config + " " + destination)

    # Change back to the original directory
    os.chdir(top_dir)


# Calls Libero and runs a script
def call_libero(libero, script):
    os.system(libero + " SCRIPT:" + script)


if __name__ == '__main__':
    # Check host system
    print("This is a " + platform.system() + " system.")

    # Set up paths for Linux and check tools are available
    if platform.system() == "Linux" or platform.system() == "Linux2":
        # The following section can be used to set up paths and environment variables used by these scripts with typical values
        # It is recommended to set these environment variables outside the script environment on the host PC
        user_home = os.path.expanduser("~")
        os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin/"
        os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin64/"
        os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/python/bin"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/riscv-unknown-elf-gcc/bin"
        os.environ["PATH"] = os.environ[
                                 "PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/jre/bin"
        os.environ["FPGENPROG"] = "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin64/fpgenprog"
        os.environ["SC_INSTALL_DIR"] = user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599"
        os.environ[
            "LM_LICENSE_FILE"] = "1703@molalla.microsemi.net:1800@molalla.microsemi.net:1717@molalla.microsemi.net" \
                                 ":1717@wilkie.microsemi.net:1800@wilkie.microsemi.net "
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

        # Tool call variables - these are the names of the tools to run which will be called from os.system. 
        # Full paths could be used here instead of assuming tools are in PATH
        mss_configurator = "pfsoc_mss"
        libero = "libero"
        softconsole_headless = "softconsole-headless"

    # Set up paths for Windows using full paths as tool names.
    # Default installation directories used below
    elif platform.system() == "win32" or platform.system() == "win64" or "_NT" in platform.system() or platform.system() == "Windows":
        mss_configurator = "C:\\Microsemi\\Libero_SoC_v2021.2\\Designer\\bin64\\pfsoc_mss.exe"
        libero = "C:\\Microsemi\\Libero_SoC_v2021.2\\Designer\\bin\\libero.exe"

        if not os.path.isfile(libero):
            print("Error: libero not found")
            exit()

        if not os.path.isfile(mss_configurator) is None:
            print("Error: polarfire soc mss configurator not found")
            exit()

    sources = {}

    # Generating the design
    print("Initializing workspace")
    init_workspace()

    print("Cloning sources")
    sources = clone_sources("sources.yaml")

    print("Generating MSS configuration")
    make_mss_config(mss_configurator, "./sources/HDL/MSS/vcs_mss.cfg", os.path.join(os.getcwd(), "output/MSS"))

    # SoftConsole headless is only available on Linux 
    # Build the HSS and bare metal using it when on Linux
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
    elif platform.system() == "win32" or platform.system() == "win64" or "_NT" in platform.system() or platform.system() == "Windows":
        print("Using pre-built HSS")
        shutil.copyfile(
            os.path.join(os.getcwd(), "sources/pre-built-executables/vcs_demo_artifacts/hss-envm-wrapper-bm1-p0.hex"),
            os.path.join(os.getcwd(), "output/HSS/hss-envm-wrapper-bm1-p0.hex"))

        print("Using pre-built bare metal")
        shutil.copyfile(
            os.path.join(os.getcwd(), "sources/pre-built-executables/vcs_demo_artifacts/mpfs-mmuart-interrupt.elf"),
            os.path.join(os.getcwd(), "./output/bare-metal/mpfs-mmuart-interrupt.elf"))

        print("Generating HSS payload")
        make_hss_payload(os.path.join(sources["HSS-payload-generator"], "hss-payload-generator/binaries/"),
                         os.path.join(os.getcwd(),
                                      "recipes/hss-payload/config_win.yaml"),
                         os.path.join(os.getcwd(), "output/payload/spi.bin"))

    print("Generating Libero project")
    print(str(os.path.join(os.getcwd(), "recipes/libero-project/generate-project.tcl")))
    call_libero(libero, os.path.join(os.getcwd(), "recipes/libero-project/generate-project.tcl"))

    print("Finished")
