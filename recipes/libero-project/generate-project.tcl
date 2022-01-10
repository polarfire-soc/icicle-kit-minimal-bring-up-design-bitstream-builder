# separate out scripts into components:
# wrapper
#   Sources
#   Design
#   Programmming 

puts [pwd]
source ./recipes/libero-project/functions.tcl
set local_dir [pwd]
set project_name libero_project
set output_directory "$local_dir/output"
set libero_project_directory "$output_directory/$project_name"
set artifact_directory "$output_directory/final-files"

# Set variables from arguments
if { $::argc > 0 } {
    set i 1
    foreach arg $::argv {
        if {[string match "*:*" $arg]} { 
            set temp [split $arg ":"]
            puts "Setting parameter [lindex $temp 0] to [lindex $temp 1]"
            set [lindex $temp 0] "[lindex $temp 1]"
        } else {
            set $arg 1
            puts "set $arg to 1"
        }
        incr i
    }
}

catch {close_project -save 1}

# Make the project
new_project \
    -location $libero_project_directory \
    -name $project_name \
    -project_description {} \
    -block_mode 0 \
    -standalone_peripheral_initialization 0 \
    -instantiate_in_smartdesign 1 \
    -ondemand_build_dh 1 \
    -use_relative_path 0 \
    -linked_files_root_dir_env {} \
    -hdl {VERILOG} \
    -family {PolarFireSoC} \
    -die {MPFS250T_ES} \
    -package {FCVG484} \
    -speed {STD} \
    -die_voltage {1.05} \
    -part_range {EXT} \
    -adv_options {IO_DEFT_STD:LVCMOS 1.8V} \
    -adv_options {RESTRICTPROBEPINS:1} \
    -adv_options {RESTRICTSPIPINS:0} \
    -adv_options {SYSTEM_CONTROLLER_SUSPEND_MODE:0} \
    -adv_options {TEMPR:EXT} \
    -adv_options {VCCI_1.2_VOLTR:EXT} \
    -adv_options {VCCI_1.5_VOLTR:EXT} \
    -adv_options {VCCI_1.8_VOLTR:EXT} \
    -adv_options {VCCI_2.5_VOLTR:EXT} \
    -adv_options {VCCI_3.3_VOLTR:EXT} \
    -adv_options {VOLTR:EXT}

# Make and import HDL sources
import_mss_component -file "./output/MSS/test_mss.cxz"

# Generate SmartDesign
cd ./sources/HDL/base
source ./base_recursive.tcl
set_root -module {base::work} 
cd ../../../

# Import constraints
source ./recipes/libero-project/constraints.tcl

# configure_tool \
#     -name {SYNTHESIZE} \
#     -params {ACTIVE_IMPLEMENTATION:synthesis} \
#     -params {AUTO_COMPILE_POINT:true} \
#     -params {BLOCK_MODE:false} \
#     -params {BLOCK_PLACEMENT_CONFLICTS:ERROR} \
#     -params {BLOCK_ROUTING_CONFLICTS:LOCK} \
#     -params {CDC_MIN_NUM_SYNC_REGS:2} \
#     -params {CDC_REPORT:true} \
#     -params {CLOCK_ASYNC:800} \
#     -params {CLOCK_DATA:5000} \
#     -params {CLOCK_GATE_ENABLE:false} \
#     -params {CLOCK_GATE_ENABLE_THRESHOLD_GLOBAL:1000} \
#     -params {CLOCK_GATE_ENABLE_THRESHOLD_ROW:100} \
#     -params {CLOCK_GLOBAL:2} \
#     -params {CREATE_IMPLEMENTATION_IDENTIFY:} 
#     -params {CREATE_IMPLEMENTATION_SYNTHESIS:synthesis} \
#     -params {PA4_GB_COUNT:36} \
#     -params {PA4_GB_MAX_RCLKINT_INSERTION:16} \
#     -params {PA4_GB_MIN_GB_FANOUT_TO_USE_RCLKINT:1000} \
#     -params {RAM_OPTIMIZED_FOR_POWER:0} \
#     -params {RETIMING:false} \
#     -params {ROM_TO_LOGIC:true} \
#     -params {SEQSHIFT_TO_URAM:1} \
#     -params {SYNPLIFY_OPTIONS:} \
#     -params {SYNPLIFY_TCL_FILE:} 

# run_tool -name {EXPORTNETLIST}

# organize_tool_files -tool {SIM_PRESYNTH} \
    -file {} \
    -module {base::work} \
    -input_type {stimulus} 

# run_tool -name {SIM_POSTSYNTH}

# Max timing work first - no high effort, no min delay
configure_tool -name {PLACEROUTE} \
    -params {DELAY_ANALYSIS:MAX} \
    -params {EFFORT_LEVEL:false} \
    -params {GB_DEMOTION:true} \
    -params {INCRPLACEANDROUTE:false} \
    -params {IOREG_COMBINING:false} \
    -params {MULTI_PASS_CRITERIA:VIOLATIONS} \
    -params {MULTI_PASS_LAYOUT:false} \
    -params {NUM_MULTI_PASSES:5} \
    -params {PDPR:false} \
    -params {RANDOM_SEED:0} \
    -params {REPAIR_MIN_DELAY:true} \
    -params {REPLICATION:false} \
    -params {SLACK_CRITERIA:WORST_SLACK} \
    -params {SPECIFIC_CLOCK:} \
    -params {START_SEED_INDEX:1} \
    -params {STOP_ON_FIRST_PASS:false} \
    -params {TDPR:true} 

run_tool -name {PLACEROUTE} 

# Check for max delay and min delay violations using timing verification

run_tool -name {VERIFYTIMING}

# if no max violations continue...

# Min delay next in incremental
configure_tool -name {PLACEROUTE} \
    -params {DELAY_ANALYSIS:MAX} \
    -params {EFFORT_LEVEL:false} \
    -params {GB_DEMOTION:true} \
    -params {INCRPLACEANDROUTE:true} \
    -params {IOREG_COMBINING:false} \
    -params {MULTI_PASS_CRITERIA:VIOLATIONS} \
    -params {MULTI_PASS_LAYOUT:false} \
    -params {NUM_MULTI_PASSES:25} \
    -params {PDPR:false} \
    -params {RANDOM_SEED:7} \
    -params {REPAIR_MIN_DELAY:true} \
    -params {REPLICATION:false} \
    -params {SLACK_CRITERIA:WORST_SLACK} \
    -params {SPECIFIC_CLOCK:} \
    -params {START_SEED_INDEX:9} \
    -params {STOP_ON_FIRST_PASS:true} \
    -params {TDPR:true}

run_tool -name {PLACEROUTE}

run_tool -name {VERIFYPOWER}

# Should stop here on violations
run_tool -name {VERIFYTIMING}

# run_tool -name {EXPORTSDF}

# organize_tool_files -tool {SIM_PRESYNTH} \
    -file {} \
    -module {base::work} \
    -input_type {stimulus} 

# run_tool -name {SIM_POSTLAYOUT}

# run_tool -name {CONFIGURE_CHAIN}

# select_programmer -programmer_id {S2011K1YJJ}

run_tool -name {GENERATEPROGRAMMINGDATA}

# Import clients
create_eNVM_config "output/clients/HSS_ENVM.cfg" "../../output/HSS/hss-envm-wrapper-bm1-p0.hex"
configure_envm -cfg_file "./output/clients/HSS_ENVM.cfg"

create_spi_config "output/clients/bare_metal_spi.cfg" "../../output/payload/spi.bin"
configure_spiflash -cfg_file "./output/clients/bare_metal_spi.cfg"
generate_design_initialization_data 


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

# Program the SPI first so the device is reset after bitstream programming to boot this payload
run_tool -name {GENERATE_SPI_FLASH_IMAGE} 
run_tool -name {PROGRAM_SPI_FLASH_IMAGE} 

configure_tool -name {CONFIGURE_ACTION_PROCEDURES} \
         -params {prog_optional_procedures:""} \
         -params {skip_recommended_procedures:""} 

run_tool -name {PROGRAMDEVICE}

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
         
