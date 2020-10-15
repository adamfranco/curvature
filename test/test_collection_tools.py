# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from copy import copy
from curvature.collection_tools import CollectionSegmentTraverser


def my_collection():
    return {
         'join_type': 'ref',
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
                                     'length': 23}]}]}

def test_traversal_advance_forward():
    traverser = CollectionSegmentTraverser(my_collection())
    assert traverser.way_index == 0
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 4

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 3
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 4
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 2
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 2
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 2
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 3
    assert traverser.has_next() == False

def test_traversal_advance_backward():
    traverser = CollectionSegmentTraverser(my_collection(), 2, 2, 'backward')
    assert traverser.way_index == 2
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 2
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 2
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 4
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 3
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 4

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == -1
    assert traverser.has_next() == False


def test_traversal_forward():
    traverser = CollectionSegmentTraverser(my_collection())
    i = 0
    while traverser.has_next():
        segment = traverser.next()
        i = i + 1
    assert i == 11

def test_traversal_backward():
    traverser = CollectionSegmentTraverser(my_collection(), 2, 2, 'backward')
    i = 0
    while traverser.has_next():
        segment = traverser.next()
        i = i + 1
    assert i == 11

def test_traversal_forward_reset_backward():
    traverser = CollectionSegmentTraverser(my_collection(), 1, 0)
    assert traverser.way_index == 1
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 4

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.advance_postion()
    assert traverser.way_index == 1
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 2

    traverser.reset_postition()
    traverser.set_direction('backward')
    assert traverser.way_index == 1
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 4

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 2
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 1
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 3

    traverser.advance_postion()
    assert traverser.way_index == 0
    assert traverser.segment_index == 0
    assert traverser.has_next() == True
    assert traverser.current()['curvature'] == 1

    traverser.advance_postion()
    assert traverser.way_index == -1
    assert traverser.has_next() == False

def test_traversal_forward_reset_backward_with_next():
    traverser = CollectionSegmentTraverser(my_collection(), 1, 0)
    segment = traverser.next()
    assert segment['curvature'] == 4

    segment = traverser.next()
    assert segment['curvature'] == 2

    segment = traverser.next()
    assert segment['curvature'] == 2

    traverser.reset_postition()
    traverser.set_direction('backward')
    segment = traverser.next()
    assert segment['curvature'] == 4

    segment = traverser.next()
    assert segment['curvature'] == 3

    segment = traverser.next()
    assert segment['curvature'] == 3

    segment = traverser.next()
    assert segment['curvature'] == 1

    assert traverser.has_next() == False
