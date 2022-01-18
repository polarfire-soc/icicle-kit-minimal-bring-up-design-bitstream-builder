import os
import yaml
import git
import requests
import zipfile
import io
import shutil
import subprocess


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
    subprocess.call(mss_configurator + ' -CONFIGURATION_FILE:' + config_file + ' -OUTPUT_DIR:' + output_dir, shell=True)


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

    # make sure the tool is executable (we download and extract it as a zip source)
    os.system("chmod +x ./hss-payload-generator")

    # Generate the payload with the output going to the output directory
    os.system("./hss-payload-generator -c " + config + " " + destination)

    # Change back to the original directory
    os.chdir(top_dir)


# Calls Libero and builds a project
def make_libero_project(libero, script):
    os.system(libero + " SCRIPT:" + script)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # The following section can be used to set up paths and environment variables used by these scripts with typical values
    # It is recommended to set these environment variables outside the script environment on the host PC
    user_home = os.path.expanduser("~")
    os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin/"
    os.environ["PATH"] = os.environ["PATH"] + ":" + "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin64/"
    os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/"
    os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/python/bin"
    os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/riscv-unknown-elf-gcc/bin"
    os.environ["PATH"] = os.environ["PATH"] + ":" + user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599/eclipse/jre/bin"
    os.environ["FPGENPROG"] = "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin64/fpgenprog"
    os.environ["SC_INSTALL_DIR"] = user_home + "/Microchip/SoftConsole-v2021.3-7.0.0.599"
    os.environ["LM_LICENSE_FILE"] = "1703@molalla.microsemi.net:1800@molalla.microsemi.net:1717@molalla.microsemi.net" \
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

    sources = {}

    # Tool call variables
    mss_configurator = "pfsoc_mss"
    libero = "libero"
    softconsole_headless = "softconsole-headless"

    # Generating the design
    print("Initializing workspace")
    init_workspace()

    print("Cloning sources")
    sources = clone_sources("sources.yaml")

    print("Generating MSS configuration")
    make_mss_config(mss_configurator, "./sources/HDL/MSS/vcs_mss.cfg", os.path.join(os.getcwd(), "output/MSS"))

    print("Building HSS")
    make_hss(sources["HSS"])

    print("Building bare metal")
    make_bare_metal(softconsole_headless, sources["bare-metal-examples"])

    print("Generating HSS payload")
    make_hss_payload(os.path.join(sources["HSS-payload-generator"], "hss-payload-generator/binaries/"),
                     os.path.join(os.getcwd(),
                                  "recipes/hss-payload/config.yaml"),
                     os.path.join(os.getcwd(), "output/payload/spi.bin"))

    print("Generating Libero project")
    make_libero_project(libero, "./recipes/libero-project/generate-project.tcl")

    print("Finished")
