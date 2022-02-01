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
