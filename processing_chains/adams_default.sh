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
reuse_temp=0
output_dir="."
verbose=""
usage="
$0 [-h] [-v] [-t temp/dir] [-o output/dir] <input-file.osm.pbf>

  -h      Show this help.
  -v      Verbose mode, print details about progress.
  -t      Use another directory for temporary files. Default: /tmp/
  -o      Use another directory for output files. Default: ./
  -r      Keep and reuse temporary files.
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
while getopts "h?vrt:o:" opt; do
  case "$opt" in
  h|\?)
    echo "$usage" >&2
    exit 1
    ;;
  v)  verbose="-v"
    ;;
  r)  reuse_temp=1
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

# Store our current working directory and the output path as variables.
cwd=`pwd`
cd $output_dir
output_dir=`pwd`
cd $cwd

##
# Process each file in the input list
##
for input_file in "$@"
do
  # Strip off the file extensions.
  filename=`basename -s .pbf $input_file`
  filename=`basename -s .osm $filename`

  if [ $reuse_temp  -eq 0 ] || [ ! -f $temp_dir/$filename.msgpack ]
  then

    # Take the following processing steps first:
    # 1. Collect the highway ways and their points into collections.
    # 2. Filter out unpaved ways and highway types we aren't interested in.
    # 3. Exclude US TIGER-imported ways that don't have names or ref tags and have not been
    #    reviewed. These are most likely driveways or forest tracks.
    # 4. Add segments and their lengths & radii.
    # 5. Calculate the curvature and filter curvature values for "deflections" (noisy data)
    # 6. Split our collections on long straight-aways (longer than 1.5 miles) to avoid
    #    highlighting long straight roads with infrequent curvy-sections.
    # 7. Sum the length and curvature of the sections in each way for reuse.
    # 8. Filter out collections not meeting our minimum curvature thresholds.
    # 9. Sort the items by their curvature value.
    # 10. Save the intermediate data.
    $script_path/curvature-collect --highway_types 'motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link,service' $verbose $input_file \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag surface --values 'unpaved,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag service --values 'driveway,parking_aisle,drive-through,parking,bus,emergency_access' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEmpty("name"), TagEmpty("ref"), TagEquals("highway", "residential"), TagEquals("tiger:reviewed", "no"))' \
      | $script_path/curvature-pp add_segments \
      | $script_path/curvature-pp add_segment_length_and_radius \
      | $script_path/curvature-pp add_segment_curvature \
      | $script_path/curvature-pp filter_segment_deflections \
      | $script_path/curvature-pp squash_curvature_for_tagged_ways --tag junction --values 'roundabout,circular' \
      | $script_path/curvature-pp squash_curvature_near_way_tag_change --tag junction --only-values 'roundabout,circular' --distance 30 \
      | $script_path/curvature-pp squash_curvature_near_way_tag_change --tag oneway --ignored-values 'no' --distance 30 \
      | $script_path/curvature-pp split_collections_on_straight_segments --length 2414 \
      | $script_path/curvature-pp roll_up_length \
      | $script_path/curvature-pp roll_up_curvature \
      | $script_path/curvature-pp filter_collections_by_curvature --min 300 \
      | $script_path/curvature-pp sort_collections_by_sum --key curvature --direction DESC \
      > $temp_dir/$filename.msgpack
  else
    if [[ $verbose == '-v' ]]
    then
      echo "Reusing temp files.."
    fi
  fi

  # Output a KML file showing only the most twisty roads, those with a curvature
  # of 1000 or more.
  if [[ $verbose == '-v' ]]
  then
    echo "Preparing $filename.c_1000.kmz ..."
  fi
  # Make a temporary directory.
  mkdir $temp_dir/$filename
  # Filter and write the KML.
  cat $temp_dir/$filename.msgpack \
    | $script_path/curvature-pp filter_collections_by_curvature --min 1000 \
    | $script_path/curvature-output-kml --min_curvature 1000 --max_curvature 20000 \
    > $temp_dir/$filename/doc.kml
  # Add our key icon.
  mkdir $temp_dir/images
  cp ${script_path}/../output-master/legend.png $temp_dir/images/legend.png
  # Zip the KML into a KMZ
  cd $temp_dir
  zip -q $output_dir/$filename.c_1000.kmz $filename/doc.kml images/legend.png
  # Delete our temporary files
  rm $filename/doc.kml
  rm images/legend.png
  rmdir images
  rmdir $filename
  cd $cwd

  # Output a KML file showing moderately twisty roads, those with a curvature
  # of 300 or more.
  if [[ $verbose == '-v' ]]
  then
    echo "Preparing $filename.c_300.kmz ..."
  fi
  # Make a temporary directory.
  mkdir $temp_dir/$filename
  # Add our key icon.
  mkdir $temp_dir/images
  cp ${script_path}/../output-master/legend.png $temp_dir/images/legend.png
  # Filter and write the KML.
  cat $temp_dir/$filename.msgpack \
    | $script_path/curvature-output-kml --min_curvature 300 --max_curvature 20000 \
    > $temp_dir/$filename/doc.kml
  # Add our key icon.
  mkdir $temp_dir/images
  cp ${script_path}/../output-master/legend.png $temp_dir/images/legend.png
  # Zip the KML into a KMZ
  cd $temp_dir
  zip -q $output_dir/$filename.c_300.kmz $filename/doc.kml images/legend.png
  # Delete our temporary file.
  rm $filename/doc.kml
  rm images/legend.png
  rmdir images
  rmdir $filename
  cd $cwd

  # Output a KML file showing only the most twisty roads, with the curve radii
  # colored. We'll only include the most twisty roads (curvature >= 1000).
  if [[ $verbose == '-v' ]]
  then
    echo "Preparing $filename.c_1000.curves.kmz ..."
  fi
  # Make a temporary directory.
  mkdir $temp_dir/$filename
  # Filter and write the KML.
  cat $temp_dir/$filename.msgpack \
     | $script_path/curvature-pp filter_collections_by_curvature --min 1000 \
     | $script_path/curvature-output-kml-curve-radius \
     > $temp_dir/$filename/doc.kml
  # Zip the KML into a KMZ
  cd $temp_dir
  zip -q $output_dir/$filename.c_1000.curves.kmz $filename/doc.kml
  # Delete our temporary file.
  rm $filename/doc.kml
  rmdir $filename
  cd $cwd

  if [[ ! reuse_temp ]]
  then
    rm $temp_dir/$filename.msgpack
  fi
done
