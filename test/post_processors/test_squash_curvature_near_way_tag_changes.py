# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from curvature.post_processors.squash_curvature_near_way_tag_change import SquashCurvatureNearWayTagChange
from copy import copy

def roads():
    return [
        {'join_type': 'none',
         'ways': [{ 'id': 1,
                    'tags': {
                        'name':     'Road 1',
                        'highway':  'unclassified'},
                    'segments': [ {'curvature': 2,
                                   'length': 30}]}]},
        {'join_type': 'ref',
         'ways': [{ 'id': 2,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 50},
                                    {'curvature': 3,
                                     'curvature_level': 2,
                                     'length': 25},
                                    {'curvature': 3,
                                     'curvature_level': 2,
                                     'length': 10}]},
                  { 'id': 3,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'curvature': 14,
                    'segments': [   {'curvature': 4,
                                     'curvature_level': 4,
                                     'length': 20},
                                    {'curvature': 2,
                                     'curvature_level': 2,
                                     'length': 50},
                                    {'curvature': 2,
                                     'curvature_level': 2,
                                     'length': 50},
                                     {'curvature': 2,
                                      'curvature_level': 2,
                                      'length': 50},
                                    {'curvature': 3,
                                     'curvature_level': 3,
                                     'length': 13}]},
                  { 'id': 4,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 13},
                                    {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 19},
                                    {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 23}]}]},
        {'join_type': 'none',
         'ways': [{ 'id': 6,
                    'tags': {
                        'name':     'My Other Highway',
                        'ref':      'US 1235',
                        'highway':  'secondary'},
                    'segments': [   {'curvature': 3},
                                    {'curvature': 3}]}]},
    ]

def test_normal_ways():
    data = roads()
    result = list(SquashCurvatureNearWayTagChange(tag='oneway', ignored_values=['no'], distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 3
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 4
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 3
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_oneway_transition():
    data = roads()
    data[1]['ways'][1]['tags']['oneway'] = 'yes'
    result = list(SquashCurvatureNearWayTagChange(tag='oneway', ignored_values=['no'], distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][3]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_no_failure_if_curvature_not_always_set():
    data = roads()
    data[1]['ways'][1]['tags']['oneway'] = 'yes'
    del data[1]['ways'][1]['curvature']
    del data[1]['ways'][1]['segments'][1]['curvature']
    result = list(SquashCurvatureNearWayTagChange(tag='oneway', ignored_values=['no'], distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert 'curvature' not in result[1]['ways'][1]['segments'][1].keys()
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][3]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3
