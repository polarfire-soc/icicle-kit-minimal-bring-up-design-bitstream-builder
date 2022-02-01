source ./recipes/libero-project/configure.tcl

open_project -file {./output/libero_project/libero_project.prjx} -do_backup_on_convert 1 -backup_file {./output/libero_project/libero_project.zip} 

# Import clients
create_eNVM_config "output/clients/HSS_ENVM.cfg" "../../output/HSS/hss-envm-wrapper-bm1-p0.hex"
configure_envm -cfg_file "./output/clients/HSS_ENVM.cfg"

create_spi_config "output/clients/bare_metal_spi.cfg" "../../output/payload/spi.bin"
configure_spiflash -cfg_file "./output/clients/bare_metal_spi.cfg"
generate_design_initialization_data 

save_project 
