bin/curvature-pp filter_out_ways_with_tag --tag surface --values 'unpaved,dirt,gravel,fine_gravel,sand,grass,ground,pebblestone,mud,clay,dirt/sand,soil' \
| bin/curvature-pp filter_out_ways_with_tag --tag service --values 'driveway,parking_aisle,drive-through,parking,bus,emergency_access' \
| bin/curvature-pp add_segments \
| bin/curvature-pp add_segment_length_and_radius \
| bin/curvature-pp add_segment_curvature \
| bin/curvature-pp filter_segment_deflections \
| bin/curvature-pp split_collections_on_straight_segments --length 2414 \
| bin/curvature-pp add_way_length \
| bin/curvature-pp add_way_curvature \
| bin/curvature-pp filter_collections_by_curvature --min 300 \
| bin/curvature-pp sort_collections_by_sum --key curvature --direction DESC \