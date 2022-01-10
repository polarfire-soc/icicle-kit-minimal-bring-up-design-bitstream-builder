create_links \
         -convert_EDN_to_HDL 0 \
         -io_pdc ./sources/HDL/Constraints/mmuart0.pdc

organize_tool_files \
    -tool {PLACEROUTE} \
    -file ./sources/HDL/Constraints/mmuart0.pdc \
    -module {base::work} \
    -input_type {constraint}
    
