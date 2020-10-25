# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from curvature.post_processors.squash_curvature_for_ways import SquashCurvatureForWays
from copy import copy

def roads():
    return [
        {'join_type': 'none',
         'ways': [{ 'id': 1,
                    'tags': {
                        'name':     'Road 1',
                        'highway':  'unclassified'},
                    'curvature': 2,
                    'segments': [ {'curvature': 2}]}]},
        {'join_type': 'ref',
         'ways': [{ 'id': 2,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'curvature': 4,
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1},
                                    {'curvature': 3,
                                     'curvature_level': 2}]},
                  { 'id': 3,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'curvature': 7,
                    'segments': [   {'curvature': 4,
                                     'curvature_level': 4},
                                    {'curvature': 3,
                                     'curvature_level': 3}]},
                  { 'id': 4,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'curvature': 1,
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1},
                                    {'curvature': 0,
                                     'curvature_level': 0}]}]},
        {'join_type': 'none',
         'ways': [{ 'id': 6,
                    'tags': {
                        'name':     'My Other Highway',
                        'ref':      'US 1235',
                        'highway':  'secondary'},
                    'curvature': 6,
                    'segments': [   {'curvature': 3},
                                    {'curvature': 3}]}]},
    ]

def test_normal_ways():
    data = roads()
    result = list(SquashCurvatureForWays('TagAndValueRegex("^junction$", "^(roundabout|circular)$")').process(data))
    assert result[0]['ways'][0]['curvature'] == 2
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['curvature'] == 4
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][1]['curvature'] == 7
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 4
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 3
    assert result[1]['ways'][2]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[2]['ways'][0]['curvature'] == 6
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_roundabout_ways():
    data = roads()
    data[1]['ways'][1]['tags']['junction'] = 'roundabout'
    result = list(SquashCurvatureForWays('TagAndValueRegex("^junction$", "^(roundabout|circular)$")').process(data))
    assert result[0]['ways'][0]['curvature'] == 2
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['curvature'] == 4
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][2]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[2]['ways'][0]['curvature'] == 6
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_parking_lane():
    data = roads()
    data[1]['ways'][1]['tags']['parking:lane:left'] = 'parallel'
    result = list(SquashCurvatureForWays('TagAndValueRegex("^parking:lane:(both|left|right)", "parallel|diagonal|perpendicular|marked")').process(data))
    assert result[0]['ways'][0]['curvature'] == 2
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['curvature'] == 4
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][2]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[2]['ways'][0]['curvature'] == 6
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_parking_lane():
    data = roads()
    data[1]['ways'][1]['tags']['parking:lane:left:parallel'] = 'half_on_kerb'
    result = list(SquashCurvatureForWays('TagAndValueRegex("^parking:lane:(both|left|right):(parallel|diagonal|perpendicular)", "^(on_street|on_kerb|half_on_kerb|painted_area_only)$")').process(data))
    assert result[0]['ways'][0]['curvature'] == 2
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['curvature'] == 4
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][2]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[2]['ways'][0]['curvature'] == 6
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_no_failure_if_curvature_not_always_set():
    data = roads()
    data[1]['ways'][1]['tags']['junction'] = 'roundabout'
    del data[1]['ways'][1]['curvature']
    del data[1]['ways'][1]['segments'][1]['curvature']
    result = list(SquashCurvatureForWays('TagAndValueRegex("^junction$", "^(roundabout|circular)$")').process(data))
    assert result[0]['ways'][0]['curvature'] == 2
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['curvature'] == 4
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert 'curvature' not in result[1]['ways'][1].keys()
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert 'curvature' not in result[1]['ways'][1]['segments'][1].keys()
    assert result[1]['ways'][2]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[2]['ways'][0]['curvature'] == 6
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3
