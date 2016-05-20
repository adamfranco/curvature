# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from curvature.post_processors.filter_out_ways import FilterOutWays

from copy import copy

@pytest.fixture
def raymond_road():
    return {
        'join_type': 'name',
        'join_data': 'Raymond Road',
        'ways': [
            { 'id': 100000,
              'tags': {   'highway': 'residential',
                          'name': 'Raymond Road',
                          'tiger:reviewed': 'no'},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            },
            { 'id': 100001,
              'tags': {   'highway': 'unclassified',
                          'name': 'Raymond Road'},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            },
            { 'id': 100002,
              'tags': {   'highway': 'unclassified',
                          'name': 'Raymond Road',
                          'surface': 'concrete',
                          'bridge': 'yes',
                          'layer': 1},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            },
            { 'id': 100004,
              'tags': {   'highway': 'unclassified',
                          'name': 'Raymond Road',
                          'surface': 'asphalt'},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            },
            { 'id': 100005,
              'tags': {   'highway': 'tertiary',
                          'name': 'Raymond Road',},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            }]}

# A driveway or other unamed way
@pytest.fixture
def driveway():
    return {
        'join_type': 'none',
        'ways': [
            { 'id': 400000,
              'tags': {   'highway': 'residential',
                          'tiger:reviewed': 'no'},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            }]}

# "Old Mountain Road".
@pytest.fixture
def old_mountain_road():
    return {
        'join_type': 'none',
        'ways': [
            { 'id': 200000,
              'tags': {   'highway': 'residential',
                          'name': 'Old Mountain Road',
                          'tiger:reviewed': 'no'},
              'coords': [],   # Not used in this component, leaving empty for simplicity.
              'refs': []    # Not used in this component, leaving empty for simplicity.
            }]}

def test(raymond_road, driveway, old_mountain_road):
    data = [raymond_road, driveway, old_mountain_road]
    expected_result = [copy(raymond_road), copy(old_mountain_road)]

    result = list(FilterOutWays('And(TagEmpty("name"), TagEmpty("ref"), TagEquals("highway", "residential"), TagEquals("tiger:reviewed", "no"))').process(data))

    assert(result == expected_result)
    assert(len(result) == 2)
    assert(len(result[0]['ways']) == 5)
    assert(len(result[1]['ways']) == 1)
