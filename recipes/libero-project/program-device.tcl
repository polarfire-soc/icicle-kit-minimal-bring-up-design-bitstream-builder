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

open_project -file {./output/libero_project/libero_project.prjx} -do_backup_on_convert 1 -backup_file {./output/libero_project/libero_project.zip} 

# configure_tool \
         -name {IO_PROGRAMMING_STATE} \
         -params {ios_file:} 

# configure_tool \
         -name {CONFIGURE_PROG_OPTIONS} \
         -params {back_level_version:0} \
         -params {design_version:0} \
         -params {silicon_signature:} 

# configure_tool \
         -name {SPM} \
         -params {back_level_protection:true} \
         -params {debug_passkey:} \
         -params {disable_authenticate_action:false} \
         -params {disable_autoprog_iap_services:false} \
         -params {disable_debug_jtag_boundary_scan:false} \
         -params {disable_debug_read_temp_volt:false} \
         -params {disable_debug_ujtag:false} \
         -params {disable_ext_zeroization:false} \
         -params {disable_external_digest_check:false} \
         -params {disable_jtag:false} \
         -params {disable_program_action:false} \
         -params {disable_puf_emulation:false} \
         -params {disable_smartdebug_debug:false} \
         -params {disable_smartdebug_live_probe:false} \
         -params {disable_smartdebug_snvm:false} \
         -params {disable_spi_slave:false} \
         -params {disable_user_encryption_key_1:false} \
         -params {disable_user_encryption_key_2:false} \
         -params {disable_verify_action:false} \
         -params {envm_update_protection:open} \
         -params {fabric_update_protection:open} \
         -params {security_factory_access:open} \
         -params {security_key_mode:default} \
         -params {user_encryption_key_1:} \
         -params {user_encryption_key_2:} \
         -params {user_passkey_1:} \
         -params {user_passkey_2:} 

run_tool -name {GENERATEPROGRAMMINGFILE} 

# Program the SPI first so the device is reset after bitstream programming to boot the payload
run_tool -name {GENERATE_SPI_FLASH_IMAGE} 
run_tool -name {PROGRAM_SPI_FLASH_IMAGE} 

configure_tool -name {CONFIGURE_ACTION_PROCEDURES} \
         -params {prog_optional_procedures:""} \
         -params {skip_recommended_procedures:""} 

run_tool -name {PROGRAMDEVICE}

save_project 
