proc create_eNVM_config {config client} {
    set envm_config [open $config w]
    
    puts $envm_config "set_plain_text_client \\"
    puts $envm_config "-client_name {BOOT_MODE_1_ENVM_CLIENT} \\"
    puts $envm_config "-number_of_bytes 117248 \\"
    puts $envm_config "-content_type {MEMORY_FILE} \\"
    puts $envm_config "-content_file_format {Intel-Hex} \\"
    puts $envm_config "-content_file {$client} \\"
    puts $envm_config "-mem_file_base_address {0x20220000} \\"
    puts $envm_config "-start_page 0 \\"
    puts $envm_config "-use_for_simulation 0 \\"
    puts $envm_config "-reprogram 1 \\"
    puts $envm_config "-use_as_rom 0 \\"
    puts $envm_config "-fabric_access_read 1 \\"
    puts $envm_config "-fabric_access_write 0 \\"
    puts $envm_config "-mss_access_read 1 \\"
    puts $envm_config "-mss_access_write 0"

    close $envm_config
}

proc create_spi_config {config client} {
    set spi_config [open $config w]
    
    puts $spi_config "set_auto_update_mode {0} "
    puts $spi_config "set_spi_flash_memory_size {134217728} "
    puts $spi_config "set_client \\"
    puts $spi_config "	 -client_name    {baremetal} \\"
    puts $spi_config "	 -client_type    {FILE_DATA_STORAGE_PLAIN_BIN} \\"
    puts $spi_config "	 -content_type   {MEMORY_FILE} \\"
    puts $spi_config "	 -content_file   {$client} \\"
    puts $spi_config "	 -start_address  {1024} \\"
    puts $spi_config "	 -client_size    {16496} \\"
    puts $spi_config "	 -program        {1}"

    close $spi_config
}
