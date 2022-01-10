
import os
import yaml
import git
import requests
import zipfile
import io
import shutil
import subprocess
import hashlib


def generate_hash(file):
    BLOCK_SIZE = 65536 # The size of each read from the file
    file_hash = hashlib.sha256() # Create the hash object, can use something other than `.sha256()` if you wish
    with open(file, 'rb') as f: # Open the file to read it's bytes
        fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
        while len(fb) > 0: # While there is still data being read from the file
            file_hash.update(fb) # Update the hash
            fb = f.read(BLOCK_SIZE) # Read the next block from the file

    print (file_hash.hexdigest()) # Get the hexadecimal digest of the hash
    return file_hash.hexdigest()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Update to also init enviroment variables
def init_workspace():
    if not os.path.exists("./sources"):
        os.mkdir("./sources")

    if os.path.exists("./output"):
        shutil.rmtree('./output')
    os.mkdir("./output")
    os.mkdir("./output/MSS")
    os.mkdir("./output/HSS")
    os.mkdir("./output/bare-metal")
    os.mkdir("./output/payload")
    os.mkdir("./output/clients")
    os.mkdir("./output/final-files")
    # delete all folders in workspace


# clones the sources specified in the sources.yaml file
def clone_sources(source_list):
    source_directories = {}
    with open(source_list) as f: # open the yaml file passed as an arg
        data = yaml.load(f, Loader=yaml.FullLoader)

        keys = data.keys()
        for source in keys: # each entry in the file is a source
            if "git" in data.get(source).get("type"): # Check if this is a git source
                if os.path.exists(os.path.join("./sources", source)): # Check if we've already cloned the repo
                    repo = git.Repo.init(os.path.join("./sources", source)) # set up repo
                    repo.git.checkout(data.get(source).get("branch")) # checkout the branch from the yaml file
                    repo.remotes.origin.pull() # pull changes
                else:
                    repo = git.Repo.clone_from(data.get(source).get("link"), os.path.join("./sources", source), branch=data.get(source).get("branch")) # if we don't already have the repo, clone it
                if "commit" in data.get(source): # check if a specific commit from this branch is required
                    repo.git.checkout(data.get(source).get("commit")) # check out a specific commit
            elif "zip" in data.get(source).get("type"): # Check if this is source is a url to a zip
                if os.path.exists(os.path.join("./sources", source)): # if we already have a source of the same name delete it - can't check versions
                    shutil.rmtree(os.path.join("./sources", source))
                r = requests.get(data.get(source).get("link")) # download zip
                z = zipfile.ZipFile(io.BytesIO(r.content)) # extract zip
                z.extractall(os.path.join("./sources", source)) # save contents
            source_directories[source] = os.path.join("./sources", source) # Generate a dictionary of all of the sources that were cloned

    return source_directories


# calls the MSS configurator and generates an MSS configuration in a directory based on a cfg file
def make_mss_config(mss_configurator, config_file, output_dir):
    subprocess.call(mss_configurator + ' -CONFIGURATION_FILE:' + config_file + ' -OUTPUT_DIR:' + output_dir, shell=True)


# Builds the HSS using a pre-defined config file using SoftConsole in headless mode
def make_hss(hss_source):
    # Update XML in HSS project
    os.remove(os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))
    shutil.copyfile("./output/MSS/test_mss_mss_cfg.xml", os.path.join(hss_source, "boards/mpfs-icicle-kit-es/soc_fpga_design/xml/ICICLE_MSS_mss_cfg.xml"))
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
    # set enviroment variables
    PATH = os.environ["PATH"]
    PATH = PATH + ":$HOME/Microchip/SoftConsole-v2021.3/python/bin:$HOME/Microchip/SoftConsole-v2021.3/riscv-unknown-elf-gcc/bin:$HOME/Microchip/SoftConsole-v2021.3/eclipse/jre/bin"
    # Make the HSS
    os.system("export PATH=" + PATH + " && export SC_INSTALL_DIR=$HOME/Microchip/SoftConsole-v2021.3 && export FPGENPROG=/usr/local/microsemi/Libero_SoC_v2021.2/Libero/bin64/fpgenprog &&" + softconsole_headless + softconsole_call)
    # copy the build artifact to the output directory
    shutil.copyfile("./sources/HSS/Default/bootmode1/hss-envm-wrapper-bm1-p0.hex", "./output/HSS/hss-envm-wrapper-bm1-p0.hex")


# builds a bare metal project using softconsole
def make_bare_metal(softconsole_headless, bare_metal_source):
    # build the softconsole call
    workspace = " --workspace=" + os.path.join(os.getcwd(), "output", "bare-metal", "workspace")
    project = " --import=" + os.path.join(bare_metal_source, "driver-examples/mss/mss-mmuart/mpfs-mmuart-interrupt/")
    build = " --build=mpfs-mmuart-interrupt/DDR-Release"
    native = " --native"
    softconsole_call = workspace + project + build + native
    # Set environment variables
    PATH = os.environ["PATH"]
    PATH = PATH + ":$HOME/Microchip/SoftConsole-v2021.3/python/bin:$HOME/Microchip/SoftConsole-v2021.3/riscv-unknown-elf-gcc/bin:$HOME/Microchip/SoftConsole-v2021.3/eclipse/jre/bin"
    # build the project
    os.system("export PATH=" + PATH + " && " + softconsole_headless + softconsole_call)
    # copy the project output to the output directory
    shutil.copyfile("./sources/bare-metal-examples/driver-examples/mss/mss-mmuart/mpfs-mmuart-interrupt/DDR-Release/mpfs-mmuart-interrupt.elf", "./output/bare-metal/mpfs-mmuart-interrupt.elf" )


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
def make_libero_project(libero, script, libero_license):
    os.system("export LM_LICENSE_FILE=" + libero_license + " && " + libero + " SCRIPT:" + script)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    PATH = os.environ["PATH"]
    PATH = PATH + ":$HOME/Microchip/SoftConsole-v2021.1/python/bin:$HOME/Microchip/SoftConsole-v2021.1/riscv-unknown-elf-gcc/bin"
    os.environ["PATH"] = PATH
    sources = {}
    libero_install_directory = "/usr/local/microsemi/Libero_SoC_v2021.2/Libero/"
    mss_configurator = os.path.join(libero_install_directory, "bin64/pfsoc_mss")
    libero = os.path.join(libero_install_directory, "bin/libero")
    libero_license = "1703@molalla.microsemi.net:1800@molalla.microsemi.net:1717@molalla.microsemi.net:1717@wilkie.microsemi.net:1800@wilkie.microsemi.net"
    softconsole_headless = "/home/hugh/Microchip/SoftConsole-v2021.3/eclipse/softconsole-headless"
    file_hashes = {}

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
    make_hss_payload(os.path.join(sources["HSS-payload-generator"], "hss-payload-generator/binaries/"), os.path.join(os.getcwd(),
                                                                                                                     "recipes/hss-payload/config.yaml"), os.path.join(os.getcwd(), "output/payload/spi.bin"))

    print("Generating Libero project")
    make_libero_project(libero, "./recipes/libero-project/generate-project.tcl", libero_license)

    # for file in os.listdir("./output/final-files"):
    #     file_hashes[file] = generate_hash(os.path.join("./output/final-files", file))
    #
    # report = open ("report.txt", "a+")
    # for hash in file_hashes:
    #     print(str(hash) + ": " + str(file_hashes[hash]))
    #     report.write(str(hash) + ": " + str(file_hashes[hash]) + "\n")

  #  report.close()
