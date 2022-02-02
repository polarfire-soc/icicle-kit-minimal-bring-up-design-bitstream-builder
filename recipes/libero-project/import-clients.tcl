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

source ./recipes/libero-project/configure.tcl

open_project -file {./output/libero_project/libero_project.prjx} -do_backup_on_convert 1 -backup_file {./output/libero_project/libero_project.zip} 

# Import clients
create_eNVM_config "output/clients/HSS_ENVM.cfg" "../../output/HSS/hss-envm-wrapper-bm1-p0.hex"
configure_envm -cfg_file "./output/clients/HSS_ENVM.cfg"

create_spi_config "output/clients/bare_metal_spi.cfg" "../../output/payload/spi.bin"
configure_spiflash -cfg_file "./output/clients/bare_metal_spi.cfg"
generate_design_initialization_data 

save_project 
