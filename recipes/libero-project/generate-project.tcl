source ./recipes/libero-project/configure.tcl

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

save_project 
