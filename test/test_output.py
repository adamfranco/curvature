# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from curvature.output import KmlOutput
from copy import copy

@pytest.fixture
def road_a():
    # Note that length, radius, and curvature do not actually match the coordinates in this
    # synthetic test data. They are added to test that they remain in the output data.
    return {'id':   1000,
            'tags': {   'name':     'Road A',
                        'highway':  'unclassified',
                        'ref': 'VT-555;US-1'},
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
                        'highway':  'unclassified',
                        'ref':      'VT-555'},
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

def test_get_collection_segments(road_a, road_b):
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    segments = output.tools.get_collection_segments(collection)
    assert len(segments) == 13
    assert segments[0]['start'][0] == 44.47486310000014
    assert segments[12]['start'][0] == 44.57721230000033

def test_get_collection_curvature(road_a, road_b):
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    curvature = output.tools.get_collection_curvature(collection)
    assert curvature == 750

def test_get_collection_curvature_on_way(road_a, road_b):
    output = KmlOutput('km')
    # Set a different curvature for road_b: 300 instead of 226
    road_b['curvature'] = 300
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    curvature = output.tools.get_collection_curvature(collection)
    assert curvature == 824

def test_get_collection_length(road_a, road_b):
    # road_a length == 4030
    # road_b length == 2160
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    length = output.tools.get_collection_length(collection)
    assert length == 6190

def test_get_collection_length_on_way(road_a, road_b):
    # road_a length == 4030
    # road_b length == 2160
    output = KmlOutput('km')
    # Set a different curvature for road_b: 4000 instead of 2160
    road_b['length'] = 4000
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    length = output.tools.get_collection_length(collection)
    assert length == 8030

def test_get_length_weighted_collection_tags(road_a, road_b):
    # road_a length == 4030
    # road_b length == 2160
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    names = output.tools.get_length_weighted_collection_tags(collection, 'name')
    assert names == ['Road A', 'Road B']

    # Ensure that reversing the ways doesn't change anything.
    collection = {'join_type': 'arbitrary', 'ways': [road_b, road_a]}
    names = output.tools.get_length_weighted_collection_tags(collection, 'name')
    assert names == ['Road A', 'Road B']

    # Ensure that giving B a larger length does change the order.
    road_b['length'] = 5000
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    names = output.tools.get_length_weighted_collection_tags(collection, 'name')
    assert names == ['Road B', 'Road A']

def test_get_length_weighted_collection_tags_many_ways(road_a, road_b):
    # road_a length == 4030
    # road_b length == 2160
    output = KmlOutput('km')
    road_c = {'id':   1002,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary',
                        'ref':      'VT-555'},
            'length': 3000}
    road_d = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'ref':      'VT-555'},
            'length': 100}

    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b, road_c, road_d]}
    names = output.tools.get_length_weighted_collection_tags(collection, 'name')
    assert names == ['Road B', 'Road A']

def test_get_shared_collection_ref(road_a, road_b):
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    refs = output.tools.get_shared_collection_refs(collection)
    assert len(refs) == 1
    assert 'VT-555' in refs

    # Ensure that if a way in the collection has no refs, there are none shared.
    road_c = {'id':   1002,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary'},
            'length': 3000}
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b, road_c]}
    refs = output.tools.get_shared_collection_refs(collection)
    assert len(refs) == 0

    # Ensure that multiple refs can be returned
    road_c = {'id':   1002,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary',
                        'ref':      'VT-555;VT-17'},
            'length': 3000}
    road_d = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'ref':      'VT-555;VT-17'},
            'length': 100}
    road_e = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'ref':      'VT-555;US-30;VT-17'},
            'length': 100}
    collection = {'join_type': 'arbitrary', 'ways': [road_c, road_d, road_e]}
    refs = output.tools.get_shared_collection_refs(collection)
    assert len(refs) == 2
    assert 'VT-555' in refs
    assert 'VT-17' in refs

def test_get_collection_name(road_a, road_b):
    # road_a length == 4030
    # road_b length == 2160
    output = KmlOutput('km')
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b]}
    name = output.tools.get_collection_name(collection)
    assert name == 'Road A (VT-555)'

    # Try with additional ways that make 'Road B' longer.
    road_c = {'id':   1002,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary',
                        'ref':      'VT-555;VT-17'},
            'length': 3000}
    road_d = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'ref':      'VT-555;VT-17'},
            'length': 100}
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b, road_c, road_d]}
    name = output.tools.get_collection_name(collection)
    assert name == 'Road B (VT-555)'

    # Multiple route-numbers.
    road_a['tags']['ref'] = 'VT-555;VT-17'
    road_b['tags']['ref'] = 'VT-555;VT-17'
    road_e = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'ref':      'VT-555;US-30;VT-17'},
            'length': 100}
    collection = {'join_type': 'arbitrary', 'ways': [road_a, road_b, road_c, road_d, road_e]}
    name = output.tools.get_collection_name(collection)
    assert name == 'Road B (VT-555 / VT-17)' or name == 'Road B (VT-17 / VT-555)'

    # no road name
    road_f = {'id':   1004,
            'tags': {   'highway':  'unclassified'},
            'length': 100}
    collection = {'join_type': 'none', 'ways': [road_f]}
    name = output.tools.get_collection_name(collection)
    assert name == '1004'

    # ref only
    road_g = {'id':   1005,
            'tags': {   'highway':  'tertiary',
                        'ref':      'VT-555;VT-17'},
            'length': 100}
    collection = {'join_type': 'none', 'ways': [road_g]}
    name = output.tools.get_collection_name(collection)
    assert name == 'VT-555 / VT-17' or name == 'VT-17 / VT-555'

def test_get_collection_name_alt_refs():
    output = KmlOutput('km')
    # Ensure that if a way in the collection has no refs with a shared key, there are none shared.
    road_a = {'id':   1000,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'official_ref':      'C555'},
            'length': 3000}
    road_b = {'id':   1001,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary',
                        'highway_authority_ref':    'C555'},
            'length': 100}
    collection = {'join_type': 'ref', 'join_data': 'C555', 'ways': [road_a, road_b]}
    name = output.tools.get_collection_name(collection)
    assert name == 'Road A (C555)'

    # Ensure that multiple refs can be returned
    road_c = {'id':   1002,
            'tags': {   'name':     'Road B',
                        'highway':  'tertiary',
                        'official_ref':      'C555;C17'},
            'length': 3000}
    road_d = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'official_ref':      'C555',
                        'highway_authority_ref':    'C17'},
            'length': 100}
    road_e = {'id':   1003,
            'tags': {   'name':     'Road A',
                        'highway':  'tertiary',
                        'admin_ref':      'C555'},
            'length': 100}
    collection = {'join_type': 'ref', 'join_data': 'C555', 'ways': [road_c, road_d, road_e]}
    refs = output.tools.get_shared_collection_refs(collection)
    name = output.tools.get_collection_name(collection)
    assert name == 'Road B (C555)'
