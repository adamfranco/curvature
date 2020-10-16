# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from curvature.post_processors.squash_curvature_near_tagged_nodes import SquashCurvatureNearTaggedNodes
from copy import copy

def roads():
    return [
        {'join_type': 'none',
         'ways': [{ 'id': 1,
                    'tags': {
                        'name':     'Road 1',
                        'highway':  'unclassified'},
                    'segments': [ {'curvature': 2,
                                   'length': 30,
                                   'start': [0.1, 0.1],
                                   'end': [0.2, 0.2]}]}]},
        {'join_type': 'ref',
         'ways': [{ 'id': 2,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 50,
                                     'start': [1.1, 1.1],
                                     'end': [1.2, 1.2]},
                                    {'curvature': 3,
                                     'curvature_level': 2,
                                     'length': 25,
                                     'start': [1.2, 1.2],
                                     'end': [1.3, 1.3]},
                                    {'curvature': 3,
                                     'curvature_level': 2,
                                     'length': 10,
                                     'start': [1.3, 1.3],
                                     'end': [1.4, 1.4]}]},
                  { 'id': 3,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'curvature': 14,
                    'segments': [   {'curvature': 4,
                                     'curvature_level': 4,
                                     'length': 20,
                                     'start': [1.4, 1.4],
                                     'end': [1.5, 1.5]},
                                    {'curvature': 2,
                                     'curvature_level': 2,
                                     'length': 50,
                                     'start': [1.5, 1.5],
                                     'end': [1.6, 1.6]},
                                    {'curvature': 2,
                                     'curvature_level': 2,
                                     'length': 50,
                                     'start': [1.6, 1.6],
                                     'end': [1.7, 1.7]},
                                     {'curvature': 2,
                                      'curvature_level': 2,
                                      'length': 50,
                                      'start': [1.7, 1.7],
                                      'end': [1.8, 1.8]},
                                    {'curvature': 3,
                                     'curvature_level': 3,
                                     'length': 13,
                                     'start': [1.8, 1.8],
                                     'end': [1.9, 1.9]}]},
                  { 'id': 4,
                    'tags': {
                        'name':     'My Highway',
                        'ref':      'US 12345',
                        'highway':  'primary'},
                    'segments': [   {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 13,
                                     'start': [1.9, 1.9],
                                     'end': [2.0, 2.0]},
                                    {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 19,
                                     'start': [2.0, 2.0],
                                     'end': [2.1, 2.1]},
                                    {'curvature': 1,
                                     'curvature_level': 1,
                                     'length': 23,
                                     'start': [2.1, 2.1],
                                     'end': [2.2, 2.2]}]}]},
        {'join_type': 'none',
         'ways': [{ 'id': 6,
                    'tags': {
                        'name':     'My Other Highway',
                        'ref':      'US 1235',
                        'highway':  'secondary'},
                    'segments': [   {'curvature': 3,
                                     'start': [3.0, 3.0],
                                     'end': [3.1, 3.1]},
                                    {'curvature': 3,
                                     'start': [3.1, 3.1],
                                     'end': [3.2, 3.2]}]}]},
    ]

def test_normal_ways():
    data = roads()
    result = list(SquashCurvatureNearTaggedNodes(tag='highway', values=['stop','give_way','traffic_signals','crossing'], distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 3
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 3
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 4
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 2
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][3]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 3
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_stopsign_transition():
    data = roads()
    data[1]['ways'][0]['segments'][2]['end'] = [1.4, 1.4, 5000]
    data[1]['ways'][0]['nodes'] = {
        5000: {
            'tags': {
                'highway': 'stop'
            }
        }
    }
    data[1]['ways'][1]['segments'][0]['start'] = [1.4, 1.4, 5000]
    data[1]['ways'][1]['nodes'] = {
        5000: {
            'tags': {
                'highway': 'stop'
            }
        }
    }
    result = list(SquashCurvatureNearTaggedNodes(tag='highway', values=['stop','give_way','traffic_signals','crossing'], distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][3]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 3
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3

def test_stopsign_transition_any_value():
    data = roads()
    data[1]['ways'][0]['segments'][2]['end'] = [1.4, 1.4, 5000]
    data[1]['ways'][0]['nodes'] = {
        5000: {
            'tags': {
                'highway': 'stop'
            }
        }
    }
    data[1]['ways'][1]['segments'][0]['start'] = [1.4, 1.4, 5000]
    data[1]['ways'][1]['nodes'] = {
        5000: {
            'tags': {
                'highway': 'stop'
            }
        }
    }
    result = list(SquashCurvatureNearTaggedNodes(tag='highway', distance=30).process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 2
    assert result[1]['ways'][0]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][0]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][0]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][0]['segments'][2]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][0]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature'] == 0
    assert result[1]['ways'][1]['segments'][1]['curvature_level'] == 0
    assert result[1]['ways'][1]['segments'][2]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][3]['curvature'] == 2
    assert result[1]['ways'][1]['segments'][4]['curvature'] == 3
    assert result[1]['ways'][2]['segments'][0]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][1]['curvature'] == 1
    assert result[1]['ways'][2]['segments'][2]['curvature'] == 1
    assert result[2]['ways'][0]['segments'][0]['curvature'] == 3
    assert result[2]['ways'][0]['segments'][1]['curvature'] == 3
