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
