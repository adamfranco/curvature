#!/bin/sh

# surfaces.sh
#
# Output road-surface data from Open Street Map (OSM).
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
# process it and output it as a KMZ file that shows the surfaces of roads in the
# input data.
#
# Author: Adam Franco
# https://github.com/adamfranco/curvature
# Copyright 2016 Adam Franco
# License: GNU General Public License Version 3 or later

# Set some default variables:
temp_dir="/tmp"
output_dir="."
verbose=""
usage="$0 [-h] [-v] [-t temp/dir] [-o output/dir] <input-file.osm.pbf>

  -h      Show this help.
  -v      Verbose mode, print details about progress.
  -t      Use another directory for temporary files. Default: /tmp/
  -o      Use anotehr directory for output files. Default: ./
"
# Store our the program path.
pushd `dirname $0` > /dev/null
my_path=`pwd -P`
popd > /dev/null
script_path=`dirname $my_path`
script_path="${script_path}/bin"

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
  v)  verbose="-v"
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

  # Make a temporary directory.
  mkdir $temp_dir/$filename

  # Take the following processing steps first:
  # 1. Calculate the curvature
  # 2. Add 'length' fields to the data.
  # 3. Sort the items by their curvature value.
  # 3. Output a KML file showing the surfaces for all roads.
  $script_path/curvature-collect --highway_types 'motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link,service' $verbose $input_file \
    | $script_path/curvature-pp add_segments \
    | $script_path/curvature-pp add_segment_length_and_radius \
    | $script_path/curvature-output-kml-surfaces \
    > $temp_dir/$filename/doc.kml
  # Zip the KML into a KMZ
  zip -q $output_dir/$filename.surfaces.kmz $temp_dir/$filename/doc.kml
  # Delete our temporary file.
  rm $temp_dir/$filename/doc.kml
  rmdir $temp_dir/$filename

done
