# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from curvature.post_processors.filter_segment_deflections import FilterSegmentDeflections
from curvature.post_processors.add_segment_length_and_radius import AddSegmentLengthAndRadius
from curvature.post_processors.add_segment_curvature import AddSegmentCurvature
from copy import copy

@pytest.fixture
def way_deviated_a():
    # __/\__
    return { 'segments': [
                    # Straight
                    {   'start':  [44.0000, -73.0010],
                        'end':    [44.0000, -73.0008],
                        'length': 16.002394317596398,
                        'radius': 2022.4401873216705,
                        'curvature': 0,
                        'curvature_level': 0},
                    {   'start':  [44.0000, -73.0008],
                        'end':    [44.0000, -73.0007],
                        'length': 8.001338048508094,
                        'radius': 12.003004511231007,
                        'curvature': 16.002676097016188,
                        'curvature_level': 4},
                    # Bump up.
                    {   'start':  [44.0000, -73.0007],
                        'end':    [44.0001, -73.0006],
                        'length': 13.701657343862479,
                        'radius': 8.43922996173027,
                        'curvature': 27.403314687724958,
                        'curvature_level': 4},
                    # Bump down.
                    {   'start':  [44.0001, -73.0006],
                        'end':    [44.0000, -73.0005],
                        'length': 13.701657343862479,
                        'radius': 8.43922996173027,
                        'curvature': 27.403314687724958,
                        'curvature_level': 4},
                    # Straight
                    {   'start':  [44.0000, -73.0005],
                        'end':    [44.0000, -73.0004],
                        'length': 8.001338048508094,
                        'radius': 12.003004511231007,
                        'curvature': 16.002676097016188,
                        'curvature_level': 4},
                    {   'start':  [44.0000, -73.0004],
                        'end':    [44.0000, -73.0003],
                        'length': 8.001338048508094,
                        'radius': 674.1572507227743,
                        'curvature': 0,
                        'curvature_level': 0}]
            }

@pytest.fixture
def way_deviated_b():
    # __/\  __
    #     \/
    return { 'segments': [
                    # Straight segments
                    {   'start':  [44.0000, -73.0019],
                        'end':    [44.0000, -73.0018],
                        'length': 8.001338048508094,
                        'radius': 674.1572507227743,
                        'curvature': 0,
                        'curvature_level': 0},
                    {   'start':  [44.0000, -73.0018],
                        'end':    [44.0000, -73.0017],
                        'length': 8.001338048508094,
                        'radius': 12.003004511231007,
                        'curvature': 16.002676097016188,
                        'curvature_level': 4},
                    # Bump up.
                    {   'start':  [44.0000, -73.0017],
                        'end':    [44.0001, -73.0016],
                        'length': 13.701657343862479,
                        'radius': 8.43922996173027,
                        'curvature': 27.403314687724958,
                        'curvature_level': 4},
                    # Bump down.
                    {   'start':  [44.0001, -73.0016],
                        'end':    [44.0000, -73.0015],
                        'length': 13.701657343862479,
                        'radius': 8.43922996173027,
                        'curvature': 27.403314687724958,
                        'curvature_level': 4},
                    # Bump down.
                    {   'start':  [44.0000, -73.0015],
                        'end':    [43.9999, -73.0014],
                        'length': 13.70198643769922,
                        'radius': 8.439327773297176,
                        'curvature': 27.40397287539844,
                        'curvature_level': 4},
                    # Bump up.
                    {   'start':  [43.9999, -73.0014],
                        'end':    [44.0000, -73.0013],
                        'length': 13.70198643769922,
                        'radius': 8.439327773297176,
                        'curvature': 27.40397287539844,
                        'curvature_level': 4},
                    # Straight segments
                    {   'start':  [44.0000, -73.0013],
                        'end':    [44.0000, -73.0012],
                        'length': 8.001338048508094,
                        'radius': 12.00299786702176,
                        'curvature': 16.002676097016188,
                        'curvature_level': 4},
                    {   'start':  [44.0000, -73.0012],
                        'end':    [44.0000, -73.0010],
                        'length': 16.002394317596398,
                        'radius': 2022.44018732167,
                        'curvature': 0,
                        'curvature_level': 0}]
            }

def test_filter_a(way_deviated_a):
    data = [{'ways': [way_deviated_a]}]

    # result = list(AddSegmentLengthAndRadii().process(data))
    # result = list(AddSegmentCurvature().process(result))
    # segments = result[0][0]['segments']
    # assert segments == []

    result = list(FilterSegmentDeflections().process(data))
    for segment in result[0]['ways'][0]['segments']:
        assert segment['curvature'] == 0
        assert segment['curvature_level'] == 0

def test_filter_b(way_deviated_b):
    data = [{'ways': [way_deviated_b]}]

    # result = list(AddSegmentLengthAndRadii().process(data))
    # result = list(AddSegmentCurvature().process(result))
    # segments = result[0][0]['segments']
    # assert segments == []

    result = list(FilterSegmentDeflections().process(data))
    segments = result[0]['ways'][0]['segments']
    for i, segment in enumerate(segments):
        assert segment['curvature'] == 0, 'curvature should be 0 for segment {}'.format(i)
        assert segment['curvature_level'] == 0, 'curvature_level should be 0 for segment {}'.format(i)

def test_filter_b_a(way_deviated_b, way_deviated_a):
    data = [{'join_type': 'arbitrary', 'ways': [way_deviated_b, way_deviated_a]}]

    result = list(FilterSegmentDeflections().process(data))
    for i, segment in enumerate(result[0]['ways'][0]['segments']):
        assert segment['curvature'] == 0, 'curvature should be 0 for segment b {}'.format(i)
        assert segment['curvature_level'] == 0, 'curvature_level should be 0 for segment b {}'.format(i)
    for i, segment in enumerate(result[0]['ways'][1]['segments']):
        assert segment['curvature'] == 0, 'curvature should be 0 for segment a {}'.format(i)
        assert segment['curvature_level'] == 0, 'curvature_level should be 0 for segment a {}'.format(i)
