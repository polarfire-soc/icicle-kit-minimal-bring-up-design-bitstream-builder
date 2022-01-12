open_project -file {./output/libero_project/libero_project.prjx} -do_backup_on_convert 1 -backup_file {./output/libero_project/libero_project.zip} 

# Program the SPI first so the device is reset after bitstream programming to boot the payload
run_tool -name {GENERATE_SPI_FLASH_IMAGE} 
run_tool -name {PROGRAM_SPI_FLASH_IMAGE} 

configure_tool -name {CONFIGURE_ACTION_PROCEDURES} \
         -params {prog_optional_procedures:""} \
         -params {skip_recommended_procedures:""} 

run_tool -name {PROGRAMDEVICE}
