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

# organize_tool_files -tool {SIM_PRESYNTH} \
    -file {} \
    -module {base::work} \
    -input_type {stimulus} 

# run_tool -name {SIM_PRESYNTH}

# Configure synthesis options
# configure_tool \
     -name {SYNTHESIZE} \
     -params {ACTIVE_IMPLEMENTATION:synthesis} \
     -params {AUTO_COMPILE_POINT:true} \
     -params {BLOCK_MODE:false} \
     -params {BLOCK_PLACEMENT_CONFLICTS:ERROR} \
     -params {BLOCK_ROUTING_CONFLICTS:LOCK} \
     -params {CDC_MIN_NUM_SYNC_REGS:2} \
     -params {CDC_REPORT:true} \
     -params {CLOCK_ASYNC:800} \
     -params {CLOCK_DATA:5000} \
     -params {CLOCK_GATE_ENABLE:false} \
     -params {CLOCK_GATE_ENABLE_THRESHOLD_GLOBAL:1000} \
     -params {CLOCK_GATE_ENABLE_THRESHOLD_ROW:100} \
     -params {CLOCK_GLOBAL:2} \
     -params {CREATE_IMPLEMENTATION_IDENTIFY:} \
     -params {CREATE_IMPLEMENTATION_SYNTHESIS:synthesis} \
     -params {PA4_GB_COUNT:36} \
     -params {PA4_GB_MAX_RCLKINT_INSERTION:16} \
     -params {PA4_GB_MIN_GB_FANOUT_TO_USE_RCLKINT:1000} \
     -params {RAM_OPTIMIZED_FOR_POWER:0} \
     -params {RETIMING:false} \
     -params {ROM_TO_LOGIC:true} \
     -params {SEQSHIFT_TO_URAM:1} \
     -params {SYNPLIFY_OPTIONS:} \
     -params {SYNPLIFY_TCL_FILE:} 

# Run synthesis
run_tool -name {SYNTHESIZE}

# organize_tool_files -tool {SIM_POSTSYNTH} \
    -file {} \
    -module {base::work} \
    -input_type {stimulus} 

# run_tool -name {SIM_POSTSYNTH}

# Export the netlist
# run_tool -name {EXPORTNETLIST}

# Timing verification 
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

# Finial timing check - should stop here on violations
run_tool -name {VERIFYTIMING}

run_tool -name {VERIFYPOWER}

# run_tool -name {EXPORTSDF}

# organize_tool_files -tool {SIM_POSTLAYOUT} \
    -file {} \
    -module {base::work} \
    -input_type {stimulus} 

# run_tool -name {SIM_POSTLAYOUT}

# run_tool -name {CONFIGURE_CHAIN}

# select_programmer -programmer_id {S2011K1YJJ}

run_tool -name {GENERATEPROGRAMMINGDATA}

save_project 
