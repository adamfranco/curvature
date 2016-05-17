# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from curvature.post_processors.split_collections_on_straight_segments import SplitCollectionsOnStraightSegments
from copy import copy

@pytest.fixture
def road():
    # Note that length, radius, and curvature do not actually match the coordinates in this
    # synthetic test data. They are added to test that they remain in the output data.
    return {'id':   1000,
            'tags': {   'name':     'Road A',
                        'highway':  'unclassified'},
            'refs': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'coords': [ [44.47486310000014, -73.20887729999983],
                        [44.47606690000014, -73.20894139999983],
                        [44.47617410000035, -73.20894919999994],
                        [44.47721230000033, -73.20902129999995],
                        [44.47728820000014, -73.20902659999983],
                        [44.477370500000326, -73.20903419999996],
                        [44.478012899999946, -73.20909320000007],
                        [44.478329400000135, -73.20911439999983],
                        [44.47902100000032, -73.20917629999997],
                        [44.47909000000013, -73.20918349999984]],
            'segments': [
                            # Curve
                            {   'start':  [44.47486310000014, -73.20887729999983],
                                'end':    [44.47606690000014, -73.20894139999983],
                                'length': 100,
                                'radius': 150,
                                'curvature': 100,
                                'curvature_level': 1},
                            # Short straight segment
                            {   'start':  [44.47606690000014, -73.20894139999983],
                                'end':    [44.47617410000035, -73.20894919999994],
                                'length': 100,
                                'radius': 300,
                                'curvature': 0,
                                'curvature_level': 0},
                            # 2 Curved segments
                            {   'start':  [44.47617410000035, -73.20894919999994],
                                'end':    [44.47721230000033, -73.20902129999995],
                                'length': 100,
                                'radius': 90,
                                'curvature': 130,
                                'curvature_level': 2},
                            {   'start':  [44.47721230000033, -73.20902129999995],
                                'end':    [44.47728820000014, -73.20902659999983],
                                'length': 60,
                                'radius': 50,
                                'curvature': 96,
                                'curvature_level': 3},
                            # two straight segments over the threshold.
                            {   'start':  [44.47728820000014, -73.20902659999983],
                                'end':    [44.477370500000326, -73.20903419999996],
                                'length': 1500,
                                'radius': 2000,
                                'curvature': 0,
                                'curvature_level': 0},
                            {   'start':  [44.477370500000326, -73.20903419999996],
                                'end':    [44.478012899999946, -73.20909320000007],
                                'length': 2000,
                                'radius': 2000,
                                'curvature': 0,
                                'curvature_level': 0},
                            # Curves
                            {   'start':  [44.478012899999946, -73.20909320000007],
                                'end':    [44.478329400000135, -73.20911439999983],
                                'length': 100,
                                'radius': 150,
                                'curvature': 100,
                                'curvature_level': 1},
                            {   'start':  [44.478329400000135, -73.20911439999983],
                                'end':    [44.47902100000032, -73.20917629999997],
                                'length': 10,
                                'radius': 25,
                                'curvature': 20,
                                'curvature_level': 4},
                            {   'start':  [44.47902100000032, -73.20917629999997],
                                'end':    [44.47909000000013, -73.20918349999984],
                                'length': 60,
                                'radius': 90,
                                'curvature': 78,
                                'curvature_level': 2}]}

@pytest.fixture
def road_b():
    # Note that length, radius, and curvature do not actually match the coordinates in this
    # synthetic test data. They are added to test that they remain in the output data.
    return {'id':   1001,
            'tags': {   'name':     'Road B',
                        'highway':  'unclassified'},
            'refs': [10, 12, 13, 14, 15],
            'coords': [ [44.47909000000013, -73.20918349999984],
                        [44.57606690000014, -73.30894139999983],
                        [44.57617410000035, -73.30894919999994],
                        [44.57721230000033, -73.30902129999995],
                        [44.57728820000014, -73.30902659999983]],
            'segments': [
                            # Straight segment
                            {   'start':  [44.47909000000013, -73.20918349999984],
                                'end':    [44.57606690000014, -73.30894139999983],
                                'length': 1000,
                                'radius': 3000,
                                'curvature': 0,
                                'curvature_level': 0},
                            # Straight segment
                            {   'start':  [44.57606690000014, -73.30894139999983],
                                'end':    [44.57617410000035, -73.30894919999994],
                                'length': 1000,
                                'radius': 3000,
                                'curvature': 0,
                                'curvature_level': 0},
                            # 2 Curved segments
                            {   'start':  [44.57617410000035, -73.30894919999994],
                                'end':    [44.57721230000033, -73.30902129999995],
                                'length': 100,
                                'radius': 90,
                                'curvature': 130,
                                'curvature_level': 2},
                            {   'start':  [44.57721230000033, -73.30902129999995],
                                'end':    [44.57728820000014, -73.30902659999983],
                                'length': 60,
                                'radius': 50,
                                'curvature': 96,
                                'curvature_level': 3}]}

def test_fixture_data_validity(road):
    num_segments = len(road['segments'])
    assert len(road['refs']) == num_segments + 1
    assert len(road['coords']) == num_segments + 1
    for i in range(0, num_segments - 1):
        assert road['coords'][i] == road['segments'][i]['start']
        assert road['coords'][i + 1] == road['segments'][i]['end']

def test_short_and_straight(road):
    for segment in road['segments']:
        segment['curvature_level'] = 0
        segment['curvature'] = 0
        segment['length'] = 100
    data = [{'join_type': 'none', 'ways': [road]}]
    expected_result = copy(data) # No changes expected.
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert(result == expected_result)

def test_long_and_straight(road):
    for segment in road['segments']:
        segment['curvature_level'] = 0
        segment['curvature'] = 0
        segment['length'] = 1000
    data = [{'join_type': 'none', 'ways': [road]}]
    expected_result = copy(data) # No changes expected.
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert(result == expected_result)

def test_short_and_curvy(road):
    for segment in road['segments']:
        segment['curvature_level'] = 1
        segment['curvature'] = 100
        segment['length'] = 100
    data = [{'join_type': 'none', 'ways': [road]}]
    expected_result = copy(data) # No changes expected.
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert(result == expected_result)

def test_long_and_curvy(road):
    for segment in road['segments']:
        segment['curvature_level'] = 1
        segment['curvature'] = 1000
        segment['length'] = 1000
    data = [{'join_type': 'none', 'ways': [road]}]
    expected_result = copy(data) # No changes expected.
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert(result == expected_result)

def test_straight_in_the_middle(road):
    data = [{'join_type': 'none', 'ways': [road]}]
    road_copy = copy(road)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 3, "The road should have been split into 3 collections"

    # Verify that the way id and tags are kept.
    assert result[0]['ways'][0]['id'] == 1000
    assert result[1]['ways'][0]['id'] == 1000
    assert result[2]['ways'][0]['id'] == 1000
    assert result[0]['ways'][0]['tags'] == {'name': 'Road A', 'highway': 'unclassified'}
    assert result[1]['ways'][0]['tags'] == {'name': 'Road A', 'highway': 'unclassified'}
    assert result[2]['ways'][0]['tags'] == {'name': 'Road A', 'highway': 'unclassified'}

    # First collection should have 1 way with 4 segments & 5 coords/refs.
    assert len(result[0]['ways'][0]['segments']) == 4, "The first collection should have 4 segments"
    assert len(result[0]['ways'][0]['refs']) == 5, "The first collection should have 5 refs"
    assert len(result[0]['ways'][0]['coords']) == 5, "The first collection should have 5 coords"
    assert result[0]['ways'][0]['segments'][3] == road_copy['segments'][3]
    assert result[0]['ways'][0]['refs'][4] == road_copy['refs'][4]
    assert result[0]['ways'][0]['coords'][4] == road_copy['coords'][4]
    # Ensure internal consistancy between coords and segement start/end.
    assert result[0]['ways'][0]['coords'][0] == result[0]['ways'][0]['segments'][0]['start']
    assert result[0]['ways'][0]['coords'][1] == result[0]['ways'][0]['segments'][0]['end']
    assert result[0]['ways'][0]['coords'][1] == result[0]['ways'][0]['segments'][1]['start']
    assert result[0]['ways'][0]['coords'][2] == result[0]['ways'][0]['segments'][1]['end']
    assert result[0]['ways'][0]['coords'][2] == result[0]['ways'][0]['segments'][2]['start']
    assert result[0]['ways'][0]['coords'][3] == result[0]['ways'][0]['segments'][2]['end']
    assert result[0]['ways'][0]['coords'][3] == result[0]['ways'][0]['segments'][3]['start']
    assert result[0]['ways'][0]['coords'][4] == result[0]['ways'][0]['segments'][3]['end']

    # Second collection should have 1 way with 2 segments & 3 coords/refs.
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert len(result[1]['ways'][0]['refs']) == 3, "The second collection should have 3 refs"
    assert len(result[1]['ways'][0]['coords']) == 3, "The second collection should have 3 coords"
    # Ensure internal consistancy between coords and segement start/end.
    assert result[1]['ways'][0]['coords'][0] == result[1]['ways'][0]['segments'][0]['start']
    assert result[1]['ways'][0]['coords'][1] == result[1]['ways'][0]['segments'][0]['end']
    assert result[1]['ways'][0]['coords'][1] == result[1]['ways'][0]['segments'][1]['start']
    assert result[1]['ways'][0]['coords'][2] == result[1]['ways'][0]['segments'][1]['end']
    # Check the absolute segement, coords, and refs against our source data.
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][5]
    assert result[1]['ways'][0]['refs'][0] == road_copy['refs'][4]
    assert result[1]['ways'][0]['refs'][1] == road_copy['refs'][5]
    assert result[1]['ways'][0]['refs'][2] == road_copy['refs'][6]
    assert result[1]['ways'][0]['coords'][0] == road_copy['coords'][4]
    assert result[1]['ways'][0]['coords'][1] == road_copy['coords'][5]
    assert result[1]['ways'][0]['coords'][2] == road_copy['coords'][6]

    # Third collection should have 1 way with 3 segments & 4 coords/refs.
    assert len(result[2]['ways'][0]['segments']) == 3, "The third collection should have 3 segments"
    assert len(result[2]['ways'][0]['refs']) == 4, "The third collection should have 4 refs"
    assert len(result[2]['ways'][0]['coords']) == 4, "The third collection should have 4 coords"
    # Ensure internal consistancy between coords and segement start/end.
    assert result[2]['ways'][0]['coords'][0] == result[2]['ways'][0]['segments'][0]['start']
    assert result[2]['ways'][0]['coords'][1] == result[2]['ways'][0]['segments'][0]['end']
    assert result[2]['ways'][0]['coords'][1] == result[2]['ways'][0]['segments'][1]['start']
    assert result[2]['ways'][0]['coords'][2] == result[2]['ways'][0]['segments'][1]['end']
    assert result[2]['ways'][0]['coords'][2] == result[2]['ways'][0]['segments'][2]['start']
    assert result[2]['ways'][0]['coords'][3] == result[2]['ways'][0]['segments'][2]['end']
    # Check the absolute segement, coords, and refs against our source data.
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][7]
    assert result[2]['ways'][0]['segments'][2] == road_copy['segments'][8]
    assert result[2]['ways'][0]['refs'][0] == road_copy['refs'][6]
    assert result[2]['ways'][0]['refs'][1] == road_copy['refs'][7]
    assert result[2]['ways'][0]['refs'][2] == road_copy['refs'][8]
    assert result[2]['ways'][0]['refs'][3] == road_copy['refs'][9]
    assert result[2]['ways'][0]['coords'][0] == road_copy['coords'][6]
    assert result[2]['ways'][0]['coords'][1] == road_copy['coords'][7]
    assert result[2]['ways'][0]['coords'][2] == road_copy['coords'][8]
    assert result[2]['ways'][0]['coords'][3] == road_copy['coords'][9]

def test_leading_straightaway(road):
    # Make the first segment a long straight away
    road['segments'][0]['length'] = 3000
    road['segments'][0]['radius'] = 2000
    road['segments'][0]['curvature'] = 0
    road['segments'][0]['curvature_level'] = 0

    data = [{'join_type': 'none', 'ways': [road]}]
    road_copy = copy(road)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 4, "The road should have been split into 4 collections"

    # First section
    assert len(result[0]['ways'][0]['segments']) == 2, "The first collection should have 2 segments"
    assert result[0]['ways'][0]['segments'][0] == road_copy['segments'][0]
    assert result[0]['ways'][0]['segments'][1] == road_copy['segments'][1]

    # second section
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][2]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][3]

    # third section
    assert len(result[2]['ways'][0]['segments']) == 2, "The third collection should have 2 segments"
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][5]

    # fourth section
    assert len(result[3]['ways'][0]['segments']) == 3, "The fourth collection should have 3 segments"
    assert result[3]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[3]['ways'][0]['segments'][1] == road_copy['segments'][7]
    assert result[3]['ways'][0]['segments'][2] == road_copy['segments'][8]

def test_trailing_short_straightaway(road):
    # Make the first segment a long straight away
    road['segments'][8]['length'] = 100
    road['segments'][8]['radius'] = 2000
    road['segments'][8]['curvature'] = 0
    road['segments'][8]['curvature_level'] = 0

    data = [{'join_type': 'none', 'ways': [road]}]
    road_copy = copy(road)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 3, "The road should have been split into 3 collections"

    # First section
    assert len(result[0]['ways'][0]['segments']) == 4, "The first collection should have 4 segments"
    assert result[0]['ways'][0]['segments'][0] == road_copy['segments'][0]
    assert result[0]['ways'][0]['segments'][1] == road_copy['segments'][1]
    assert result[0]['ways'][0]['segments'][2] == road_copy['segments'][2]
    assert result[0]['ways'][0]['segments'][3] == road_copy['segments'][3]

    # second section
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][5]

    # third section
    assert len(result[2]['ways'][0]['segments']) == 3, "The third collection should have 3 segments"
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][7]
    assert result[2]['ways'][0]['segments'][2] == road_copy['segments'][8]

def test_trailing_long_straightaway(road):
    # Make the first segment a long straight away
    road['segments'][8]['length'] = 3000
    road['segments'][8]['radius'] = 2000
    road['segments'][8]['curvature'] = 0
    road['segments'][8]['curvature_level'] = 0

    data = [{'join_type': 'none', 'ways': [road]}]
    road_copy = copy(road)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 4, "The road should have been split into 4 collections"

    # First section
    assert len(result[0]['ways'][0]['segments']) == 4, "The first collection should have 4 segments"
    assert result[0]['ways'][0]['segments'][0] == road_copy['segments'][0]
    assert result[0]['ways'][0]['segments'][1] == road_copy['segments'][1]
    assert result[0]['ways'][0]['segments'][2] == road_copy['segments'][2]
    assert result[0]['ways'][0]['segments'][3] == road_copy['segments'][3]

    # second section
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][5]

    # third section
    assert len(result[2]['ways'][0]['segments']) == 2, "The third collection should have 2 segments"
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][7]

    # fourth section
    assert len(result[3]['ways'][0]['segments']) == 1, "The fourth collection should have 1 segments"
    assert result[3]['ways'][0]['segments'][0] == road_copy['segments'][8]

def test_trailing_short_straightaway_with_second_straight_way(road, road_b):
    # Make the first segment a long straight away
    road['segments'][8]['length'] = 500
    road['segments'][8]['radius'] = 2000
    road['segments'][8]['curvature'] = 0
    road['segments'][8]['curvature_level'] = 0

    # make road_b all straight
    for segment in road_b['segments']:
        segment['curvature_level'] = 0
        segment['curvature'] = 0
        segment['length'] = 1000

    data = [{'join_type': 'magic', 'ways': [road, road_b]}]
    road_copy = copy(road)
    road_b_copy = copy(road_b)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 4, "The road should have been split into 4 collections"

    # First section
    assert len(result[0]['ways'][0]['segments']) == 4, "The first collection should have 4 segments"
    assert result[0]['ways'][0]['segments'][0] == road_copy['segments'][0]
    assert result[0]['ways'][0]['segments'][1] == road_copy['segments'][1]
    assert result[0]['ways'][0]['segments'][2] == road_copy['segments'][2]
    assert result[0]['ways'][0]['segments'][3] == road_copy['segments'][3]

    # second section
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][5]

    # third section
    assert len(result[2]['ways'][0]['segments']) == 2, "The third collection should have 2 segments"
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][7]

    # fourth section
    assert len(result[3]['ways']) == 2, "The fourth collection should have 2 ways"
    assert len(result[3]['ways'][0]['segments']) == 1, "The fourth collection's first way should have 1 segment"
    assert result[3]['ways'][0]['segments'][0] == road_copy['segments'][8]
    assert len(result[3]['ways'][1]['segments']) == 4, "The fourth collection's second way should have 4 segments"
    assert result[3]['ways'][1]['segments'][0] == road_b_copy['segments'][0]
    assert result[3]['ways'][1]['segments'][1] == road_b_copy['segments'][1]
    assert result[3]['ways'][1]['segments'][2] == road_b_copy['segments'][2]
    assert result[3]['ways'][1]['segments'][3] == road_b_copy['segments'][3]

    assert result[3]['ways'][1]['coords'][0] == road_b_copy['coords'][0]
    assert result[3]['ways'][1]['coords'][-1] == road_b_copy['coords'][-1]

def test_trailing_short_straightaway_with_second_way(road, road_b):
    # Make the first segment a long straight away
    road['segments'][8]['length'] = 500
    road['segments'][8]['radius'] = 2000
    road['segments'][8]['curvature'] = 0
    road['segments'][8]['curvature_level'] = 0

    data = [{'join_type': 'magic', 'ways': [road, road_b]}]
    road_copy = copy(road)
    road_b_copy = copy(road_b)
    result = list(SplitCollectionsOnStraightSegments().process(data))
    assert len(result) == 5, "The road should have been split into 5 collections"

    # First section
    assert len(result[0]['ways'][0]['segments']) == 4, "The first collection should have 4 segments"
    assert result[0]['ways'][0]['segments'][0] == road_copy['segments'][0]
    assert result[0]['ways'][0]['segments'][1] == road_copy['segments'][1]
    assert result[0]['ways'][0]['segments'][2] == road_copy['segments'][2]
    assert result[0]['ways'][0]['segments'][3] == road_copy['segments'][3]

    # second section
    assert len(result[1]['ways'][0]['segments']) == 2, "The second collection should have 2 segments"
    assert result[1]['ways'][0]['segments'][0] == road_copy['segments'][4]
    assert result[1]['ways'][0]['segments'][1] == road_copy['segments'][5]

    # third section
    assert len(result[2]['ways'][0]['segments']) == 2, "The third collection should have 2 segments"
    assert result[2]['ways'][0]['segments'][0] == road_copy['segments'][6]
    assert result[2]['ways'][0]['segments'][1] == road_copy['segments'][7]

    # fourth section
    assert len(result[3]['ways']) == 2, "The fourth collection should have 2 ways"
    assert len(result[3]['ways'][0]['segments']) == 1, "The fourth collection's first way should have 1 segment"
    assert result[3]['ways'][0]['segments'][0] == road_copy['segments'][8]
    assert len(result[3]['ways'][1]['segments']) == 2, "The fourth collection's second way should have 2 segments"
    assert result[3]['ways'][1]['segments'][0] == road_b_copy['segments'][0]
    assert result[3]['ways'][1]['segments'][1] == road_b_copy['segments'][1]

    # fifth section
    assert len(result[4]['ways']) == 1, "The fifth collection should have 1 way"
    assert len(result[4]['ways'][0]['segments']) == 2, "The fifth collection's way should have 2 segments"
    assert result[4]['ways'][0]['segments'][0] == road_b_copy['segments'][2]
    assert result[4]['ways'][0]['segments'][1] == road_b_copy['segments'][3]
