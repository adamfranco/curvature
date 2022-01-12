#!/bin/sh

# straight-roads.sh
#
# Find straightest road segments based on Open Street Map (OSM) data.
# This is the inverse of normal curvature output.
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
# process it and output it as a trio of KMZ files that highlight the most straight
# roads in the input data.
#
# Author: Adam Franco
# https://github.com/adamfranco/curvature
# Copyright 2022 Adam Franco
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
    $script_path/curvature-collect --highway_types 'motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link,service' $verbose $input_file \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag surface --values 'unpaved,compacted,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag area --values 'yes' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag golf --values 'cartpath' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag access --values 'no' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag vehicle --values 'no' \
      | $script_path/curvature-pp filter_out_ways_with_tag --tag motor_vehicle --values 'no' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEmpty("name"), TagEmpty("ref"), TagEquals("highway", "residential"), TagEquals("tiger:reviewed", "no"))' \
      | $script_path/curvature-pp filter_out_ways --match 'And(TagEquals("highway", "raceway"), TagEquals("sport", "motocross"))' \
      | $script_path/curvature-pp add_segments \
      | $script_path/curvature-pp add_segment_length_and_radius \
      > $temp_dir/$filename.msgpack
  else
    if [[ $verbose == '-v' ]]
    then
      echo "Reusing temp files.."
    fi
  fi

  # Output a KML file showing only longest straight segments, those with a length
  # of 450m or more and whose minimum curve radius is 2000m.
  #
  # 5. Calculate the curvature to flag any curves with tighter than a 2000m radius.
  # 6. Filter curvature values for "deflections" (noisy data)
  # 7. Split our collections on short straight-aways (longer than 300 meters) to avoid
  #    highlighting curvy-sections.
  # 8. Inflate the curvature near conflict zones (intersections, etc.)
  # 9. Filter out collections with any curvature.
  # 10. Sort the items by their length value.
  # 11. Output the data.
  if [[ $verbose == '-v' ]]
  then
    echo "Preparing $filename.straight_r2000m_l450m.kmz ..."
  fi
  # Make a temporary directory.
  mkdir $temp_dir/$filename
  # Filter and write the KML.
  cat $temp_dir/$filename.msgpack \
    | $script_path/curvature-pp add_segment_curvature --l1maxr 2000 \
    | $script_path/curvature-pp filter_segment_deflections \
    | $script_path/curvature-pp inflate_curvature_for_tagged_ways --curvature=999 --tag traffic_calming \
    | $script_path/curvature-pp inflate_curvature_for_ways --curvature=999 --match 'TagAndValueRegex("^parking:lane:(both|left|right)", "parallel|diagonal|perpendicular|marked")' \
    | $script_path/curvature-pp inflate_curvature_for_ways --curvature=999 --match 'TagAndValueRegex("^parking:lane:(both|left|right):(parallel|diagonal|perpendicular)", "^(on_street|on_kerb|half_on_kerb|painted_area_only)$")' \
    | $script_path/curvature-pp inflate_curvature_near_way_tag_change --curvature=999 --tag junction --only-values 'roundabout,circular' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_way_tag_change --curvature=999 --tag oneway --ignored-values 'no' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag highway --values 'stop,give_way,traffic_signals,crossing,mini_roundabout,traffic_calming' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag traffic_calming --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag barrier --distance 30 \
    | $script_path/curvature-pp split_collections_on_straight_segments --length 300 \
    | $script_path/curvature-pp roll_up_length \
    | $script_path/curvature-pp roll_up_curvature \
    | $script_path/curvature-pp filter_collections_by_curvature --max 1 \
    | $script_path/curvature-pp sort_collections_by_sum --key length --direction DESC \
    | $script_path/curvature-pp filter_collections_by_length --min 450 \
    | $script_path/curvature-output-kml --min_curvature 0 --max_curvature 10 \
    > $temp_dir/$filename/doc.kml
  # Zip the KML into a KMZ
  cd $temp_dir
  zip -q $output_dir/$filename.straight_r2000m_l450m.kmz $filename/doc.kml
  # Delete our temporary files
  rm $filename/doc.kml
  rmdir $filename
  cd $cwd

  # Output a KML file showing only longest straight segments, those with a length
  # of 450m or more and whose minimum curve radius is 4000m.
  #
  # 5. Calculate the curvature to flag any curves with tighter than a 4000m radius.
  # 6. Filter curvature values for "deflections" (noisy data)
  # 7. Split our collections on short straight-aways (longer than 300 meters) to avoid
  #    highlighting curvy-sections.
  # 8. Inflate the curvature near conflict zones (intersections, etc.)
  # 9. Filter out collections with any curvature.
  # 10. Sort the items by their length value.
  # 11. Output the data.
  if [[ $verbose == '-v' ]]
  then
    echo "Preparing $filename.straight_r4000m_l450m.kmz ..."
  fi
  # Make a temporary directory.
  mkdir $temp_dir/$filename
  # Filter and write the KML.
  cat $temp_dir/$filename.msgpack \
    | $script_path/curvature-pp add_segment_curvature --l1maxr 4000 \
    | $script_path/curvature-pp filter_segment_deflections \
    | $script_path/curvature-pp inflate_curvature_for_tagged_ways --curvature=999 --tag traffic_calming \
    | $script_path/curvature-pp inflate_curvature_for_ways --curvature=999 --match 'TagAndValueRegex("^parking:lane:(both|left|right)", "parallel|diagonal|perpendicular|marked")' \
    | $script_path/curvature-pp inflate_curvature_for_ways --curvature=999 --match 'TagAndValueRegex("^parking:lane:(both|left|right):(parallel|diagonal|perpendicular)", "^(on_street|on_kerb|half_on_kerb|painted_area_only)$")' \
    | $script_path/curvature-pp inflate_curvature_near_way_tag_change --curvature=999 --tag junction --only-values 'roundabout,circular' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_way_tag_change --curvature=999 --tag oneway --ignored-values 'no' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag highway --values 'stop,give_way,traffic_signals,crossing,mini_roundabout,traffic_calming' --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag traffic_calming --distance 30 \
    | $script_path/curvature-pp inflate_curvature_near_tagged_nodes --curvature=999 --tag barrier --distance 30 \
    | $script_path/curvature-pp split_collections_on_straight_segments --length 300 \
    | $script_path/curvature-pp roll_up_length \
    | $script_path/curvature-pp roll_up_curvature \
    | $script_path/curvature-pp filter_collections_by_curvature --max 1 \
    | $script_path/curvature-pp sort_collections_by_sum --key length --direction DESC \
    | $script_path/curvature-pp filter_collections_by_length --min 450 \
    | $script_path/curvature-output-kml --min_curvature 0 --max_curvature 10 \
    > $temp_dir/$filename/doc.kml
  # Zip the KML into a KMZ
  cd $temp_dir
  zip -q $output_dir/$filename.straight_r4000m_l450m.kmz $filename/doc.kml
  # Delete our temporary files
  rm $filename/doc.kml
  rmdir $filename
  cd $cwd

  if [[ ! reuse_temp ]]
  then
    rm $temp_dir/$filename.msgpack
  fi
done
