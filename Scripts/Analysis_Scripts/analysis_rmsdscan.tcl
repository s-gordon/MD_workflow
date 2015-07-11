#!/usr/bin/env tclsh
# AUTHOR:   Shane Gordon
# FILE:     analysis_rmsdscan.tcl
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-18 20:40:17
# MODIFIED: 2015-07-11 22:45:51

source ../Scripts/Analysis_Scripts/common_analysis.tcl

# Sequentially read in args as $1, $2, etc.
set i 0; foreach n $argv {set [incr i] $n}

foreach index [ lsort [glob no_water_*.dcd] ] {
  regexp {0.[0-9]{1,3}} $index index_no

  # Variable definitions for later
  set seltext ${1}
  set input "no_water_$index_no"
  set out_dir "$raw/sim_$index_no"
  dir_make $out_dir
  set num_rmsf_windows 5
  set mol [ mol new $input_psf.psf type psf waitfor all ]
  set reference_CA [ atomselect $mol "$seltext and name CA" frame 0]
  set sel_protein [atomselect $mol "$seltext"]
  set sel_backbone [atomselect $mol "$seltext and backbone"]
  set sel_CA [ atomselect $mol "$seltext and name CA" ]
  mol addfile $input_psf.pdb first 0 last 0 waitfor all

  # RMSD scan
  filecheck rmsd_protein_$index_no.txt
  bigdcd rmsdscan_bigdcd $input.dcd
  bigdcd_wait
  file rename "rmsd_protein.txt" "$out_dir/rmsd_protein_$index_no.txt"
}

exit
