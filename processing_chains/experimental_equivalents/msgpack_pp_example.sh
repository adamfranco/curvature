# Store our the program path.
pushd `dirname $0` > /dev/null
my_path=`pwd -P`
popd > /dev/null
script_path=`dirname $my_path`
script_path="${script_path}/bin"

$script_path/curvature-pp filter_out_ways_with_tag --tag surface --values 'unpaved,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil' \
| $script_path/curvature-pp filter_out_ways_with_tag --tag service --values 'driveway,parking_aisle,drive-through,parking,bus,emergency_access' \
| $script_path/curvature-pp add_segments \
| $script_path/curvature-pp add_segment_length_and_radius \
| $script_path/curvature-pp add_segment_curvature \
| $script_path/curvature-pp filter_segment_deflections \
| $script_path/curvature-pp split_collections_on_straight_segments --length 2414 \
| $script_path/curvature-pp roll_up_length \
| $script_path/curvature-pp roll_up_curvature \
| $script_path/curvature-pp filter_collections_by_curvature --min 300 \
| $script_path/curvature-pp sort_collections_by_sum --key curvature --direction DESC
