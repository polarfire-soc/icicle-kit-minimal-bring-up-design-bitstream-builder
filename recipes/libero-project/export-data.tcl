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

run_tool -name {GENERATEPROGRAMMINGFILE} 

run_tool -name {GENERATEDEBUGDATA} 

export_bitstream_file \
         -file_name {bitstream_file} \
         -export_dir $artifact_directory \
         -format {DAT PPD} \
         -for_ihp 0 \
         -limit_SVF_file_size 0 \
         -limit_SVF_file_by_max_filesize_or_vectors {} \
         -svf_max_filesize {} \
         -svf_max_vectors {} \
         -master_file 0 \
         -master_file_components {} \
         -encrypted_uek1_file 0 \
         -encrypted_uek1_file_components {} \
         -encrypted_uek2_file 0 \
         -encrypted_uek2_file_components {} \
         -trusted_facility_file 1 \
         -trusted_facility_file_components {FABRIC_SNVM} \
         -zeroization_likenew_action 0 \
         -zeroization_unrecoverable_action 0 \
         -master_backlevel_bypass 0 \
         -uek1_backlevel_bypass 0 \
         -uek2_backlevel_bypass 0 \
         -master_include_plaintext_passkey 0 \
         -uek1_include_plaintext_passkey 0 \
         -uek2_include_plaintext_passkey 0 \
         -sanitize_snvm 0 \
         -sanitize_envm 0 \
         -trusted_facility_keep_fabric_operational 0 \
         -trusted_facility_skip_startup_seq 0 \
         -uek1_keep_fabric_operational 0 \
         -uek1_skip_startup_seq 0 \
         -uek2_keep_fabric_operational 0 \
         -uek2_skip_startup_seq 0 

export_prog_job \
         -job_file_name {programming_job} \
         -export_dir $artifact_directory \
         -bitstream_file_type {TRUSTED_FACILITY} \
         -bitstream_file_components {FABRIC_SNVM} \
         -zeroization_likenew_action 0 \
         -zeroization_unrecoverable_action 0 \
         -program_design 1 \
         -program_spi_flash 0 \
         -include_plaintext_passkey 0 \
         -design_bitstream_format {PPD} \
         -prog_optional_procedures {} \
         -skip_recommended_procedures {} \
         -sanitize_snvm 0 \
         -sanitize_envm 0 

export_spiflash_image \
    -file_name {spi-flash-image} \
    -export_dir $artifact_directory

export_pin_reports \
         -export_dir $artifact_directory \
         -pin_report_by_name 1 \
         -pin_report_by_pkg_pin 1 \
         -bank_report 1 \
         -io_report 1 

export_bsdl_file \
         -file $artifact_directory

update_and_run_tool -name {EXPORTDEVMEMINIT} 

export_dev_mem_init_report \
         -export_dir $artifact_directory

export_smart_debug_data \
         -file_name {smart-debug-data} \
         -export_dir $artifact_directory \
         -probes 1 \
         -package_pins 0 \
         -memory_blocks 1 \
         -envm_data 0 \
         -security_data 1 \
         -display_security_in_smartdebug 0 \
         -chain 1 \
         -programmer_settings 1 \
         -ios_states 1 \
         -generate_bitstream 0 \
         -bitstream_format {PPD} \
         -bitstream_security 0 \
         -bitstream_fabric 0 \
         -bitstream_envm 0 \
         -sanitize_envm 0 \
         -bitstream_snvm 0 \
         -sanitize_snvm 0 \
         -master_include_plaintext_passkey 0 \
         -snvm_data 1 


export_prog_job \
         -job_file_name {fp-job} \
         -export_dir $artifact_directory \
         -bitstream_file_type {TRUSTED_FACILITY} \
         -bitstream_file_components {ENVM FABRIC_SNVM} \
         -zeroization_likenew_action 0 \
         -zeroization_unrecoverable_action 0 \
         -program_design 1 \
         -program_spi_flash 0 \
         -include_plaintext_passkey 0 \
         -design_bitstream_format {PPD} \
         -prog_optional_procedures {} \
         -skip_recommended_procedures {} \
         -sanitize_snvm 0 \
         -sanitize_envm 0
         
save_project 
