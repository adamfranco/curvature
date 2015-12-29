#!/bin/sh

# curvature.sh
#
# Find roads that are the most curved or twisty based on Open Street Map (OSM) data.
#
# This directory contains a number of scripts that together form the tool-chain for
# processing OpenStreetMap (OSM) geographic data and converting it to various types
# of helpful outputs. To maintain flexibility, each of these scripts is independent
# and can be run in mostly arbitrary orders to achieve different results. After the
# OpenStreetMap "ProtocolBuffers" (.pbf) data has been read, subsequent filter and
# modification scripts read and write data from Standard-In and Standard-Out buffers
# in an intermediate "MessagePack" data format. If you'd like to modify the data in
# a slightly different way than is provided, it is relatively easy to write your own
# filter, modification script, or output script and add it to your own processing
# sequence.
#
# This shell-script is an example processing sequence that will take an input slice
# of OSM data (such as those provided by Geofabrik.de) in .pbf or .osm format then
# process it and output it as a trio of KMZ files that highlight the most twisty roads
# in the input data.
#
# Author: Adam Franco
# https://github.com/adamfranco/curvature
# Copyright 2015 Adam Franco
# License: GNU General Public License Version 3 or later

# Set some default variables:
temp_dir="/tmp"
output_dir="."
verbose=0
usage="$0 [-h] [-v] [-t temp/dir] [-o output/dir] <input-file.osm.pbf>
"
# Store our the program path.
pushd `dirname $0` > /dev/null
script_path=`pwd -P`
popd > /dev/null

##
# Allow the user to configure our variables via command-line options.
##
OPTIND=1         # Reset in case getopts has been used previously in the shell.
while getopts "h?vt:o:" opt; do
    case "$opt" in
    h|\?)
        echo usage >&2
        exit 1
        ;;
    v)  verbose=1
        ;;
		o)  output_dir=$OPTARG
        ;;
		t)  temp_dir=$OPTARG
        ;;
    esac
done
shift $((OPTIND-1))
[ "$1" = "--" ] && shift
# End configuration

##
# Process each file in the input list
##
for input_file in "$@"
do
	# Strip off the file extensions.
	filename=`basename -s .pbf $input_file`
	filename=`basename -s .osm $filename`

	# Take the following processing steps first:
	# 1. Calculate the curvature
	# 2. Add 'length' fields to the data.
	# 3. Sort the items by their curvature value.
	# 3. Save the intermediate data.
	$script_path/curvature-calculate -v $input_file \
	 | $script_path/curvature-add-length \
	 | $script_path/curvature-sort --key curvature --direction DESC \
	 > $temp_dir/$filename.msgpack

	 # Output a KML file showing only the most twisty roads, those with a curvature
	 # of 1000 or more.
	 # Make a temporary directory.
	 mkdir $temp_dir/$filename
	 # Filter and write the KML.
	 cat $temp_dir/$filename.msgpack \
	 | $script_path/curvature-filter-curvature-level --min 1000 \
	 | $script_path/curvature-output-kml --min_curvature 1000 --max_curvature 20000 \
	 > $temp_dir/$filename/doc.kml
	 # Zip the KML into a KMZ
	 zip $output_dir/$filename.c_1000.kmz $temp_dir/$filename/doc.kml
	 # Delete our temporary file.
	 rm $temp_dir/$filename/doc.kml
	 rmdir $temp_dir/$filename

	 # Output a KML file showing moderately twisty roads, those with a curvature
	 # of 300 or more.
	 # Make a temporary directory.
	 mkdir $temp_dir/$filename
	 # Filter and write the KML.
	 cat $temp_dir/$filename.msgpack \
	 | $script_path/curvature-filter-curvature-level --min 300 \
	 | $script_path/curvature-output-kml --min_curvature 300 --max_curvature 20000 \
	 > $temp_dir/$filename/doc.kml
	 # Zip the KML into a KMZ
	 zip $output_dir/$filename.c_300.kmz $temp_dir/$filename/doc.kml
	 # Delete our temporary file.
	 rm $temp_dir/$filename/doc.kml
	 rmdir $temp_dir/$filename

	 # Output a KML file showing only the most twisty roads, with the curve radii
	 # colored. We'll only include the most twisty roads (curvature >= 1000).
	 # Make a temporary directory.
	 mkdir $temp_dir/$filename
	 # Filter and write the KML.
	 cat $temp_dir/$filename.msgpack \
	 | $script_path/curvature-filter-curvature-level --min 1000 \
	 | $script_path/curvature-output-kml-curve-radius \
	 > $temp_dir/$filename/doc.kml
	 # Zip the KML into a KMZ
	 zip $output_dir/$filename.c_1000.curves.kmz $temp_dir/$filename/doc.kml
	 # Delete our temporary file.
	 rm $temp_dir/$filename/doc.kml
	 rmdir $temp_dir/$filename

	 rm $temp_dir/$filename.msgpack
done
