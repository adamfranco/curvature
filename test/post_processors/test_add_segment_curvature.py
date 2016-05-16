import pytest
from curvature.post_processors.add_segment_curvature import AddSegmentCurvature
from copy import copy

def test_straight():
    data = [{'ways': [{'segments': [{
                            'start':  [],
                            'end':    [],
                            'length': 10,
                            'radius': 200}]}]}]
    result = list(AddSegmentCurvature().process(data))
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 0

def test_level_1():
    data = [{'ways': [{'segments': [{
                            'start':  [],
                            'end':    [],
                            'length': 10,
                            'radius': 150}]}]}]
    result = list(AddSegmentCurvature().process(data))
    # Level 1 should have a weighting of '1'
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 10

def test_level_2():
    data = [{'ways': [{'segments': [{
                            'start':  [],
                            'end':    [],
                            'length': 10,
                            'radius': 90}]}]}]
    result = list(AddSegmentCurvature().process(data))
    # Level 1 should have a weighting of '1.3'
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 13

def test_level_3():
    data = [{'ways': [{'segments': [{
                            'start':  [],
                            'end':    [],
                            'length': 10,
                            'radius': 50}]}]}]
    result = list(AddSegmentCurvature().process(data))
    # Level 1 should have a weighting of '1.6'
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 16

def test_level_4():
    data = [{'ways': [{'segments': [{
                            'start':  [],
                            'end':    [],
                            'length': 10,
                            'radius': 20}]}]}]
    result = list(AddSegmentCurvature().process(data))
    # Level 1 should have a weighting of '2'
    assert result[0]['ways'][0]['segments'][0]['curvature'] == 20
