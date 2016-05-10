import pytest
from curvature.post_processors.split_collections_on_tag import SplitCollectionsOnTag
from copy import copy

@pytest.fixture
def raymond_road():
    return [
        { 'id': 100000,
          'tags': {   'highway': 'residential',
                      'name': 'Raymond Road',
                      'surface': 'asphalt'},
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
        },
    ]

# "Old Mountain Road".
# A mixture of highway types where an unclassified road becomes a track over a pass,
# then becomes an unclassified road again on the other side.
@pytest.fixture
def old_mountain_road():
    return [
        { 'id': 200000,
          'tags': {   'highway': 'unclassified',
                      'name': 'Old Mountain Road',
                      'surface': 'asphalt'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200001,
          'tags': {   'highway': 'unclassified',
                      'name': 'Old Mountain Road',
                      'surface': 'gravel'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200002,
          'tags': {   'highway': 'track',
                      'name': 'Old Mountain Road'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200003,
          'tags': {   'highway': 'track',
                      'name': 'Old Mountain Road',
                      'surface': 'concrete',
                      'bridge': 'yes',
                      'layer': 1},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200004,
          'tags': {   'highway': 'track',
                      'name': 'Old Mountain Road'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200005,
          'tags': {   'highway': 'unclassified',
                      'name': 'Old Mountain Road',
                      'surface': 'dirt'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200006,
          'tags': {   'highway': 'unclassified',
                      'name': 'Old Mountain Road',
                      'surface': 'asphalt'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 200007,
          'tags': {   'highway': 'unclassified',
                      'name': 'Old Mountain Road'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
    ]

# This road is an unclassified road that has a gravel section in the middle.
@pytest.fixture
def barnes_road():
    return [
        { 'id': 300000,
          'tags': {   'highway': 'unclassified',
                      'name': 'Barnes Road',
                      'surface': 'asphalt'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 300001,
          'tags': {   'highway': 'unclassified',
                      'name': 'Barnes Road',
                      'surface': 'gravel'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 300002,
          'tags': {   'highway': 'unclassified',
                      'name': 'Barnes Road'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        },
        { 'id': 100004,
          'tags': {   'highway': 'unclassified',
                      'name': 'Barnes Road',
                      'surface': 'asphalt'},
          'coords': [],   # Not used in this component, leaving empty for simplicity.
          'refs': []    # Not used in this component, leaving empty for simplicity.
        }
    ]

@pytest.fixture
def highway_roads():
    return ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'service', 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link']

@pytest.fixture
def surfaces_paved():
    return ['paved', 'asphalt', 'concrete', 'paving_stones', 'cobblestone', 'concrete:plates', 'sett', 'cobblestone:flattened', 'metal', 'wood', 'bricks']

@pytest.fixture
def surfaces_unpaved():
    return ['unpaved', 'dirt', 'gravel', 'fine_gravel', 'sand', 'grass', 'ground', 'pebblestone', 'mud', 'clay', 'dirt/sand', 'soil']


def test_all_roads_arent_split(raymond_road, highway_roads):
    data = [raymond_road]
    expected_result = [copy(raymond_road)]

    result = list(SplitCollectionsOnTag(tag='highway', group=highway_roads).process(data))

    assert(result == expected_result)
    assert(len(result) == 1)
    assert(len(result[0]) == 5)

def test_road_track_split(old_mountain_road, highway_roads):
    data = [old_mountain_road]
    expected_result = [ [ copy(old_mountain_road[0]),
                          copy(old_mountain_road[1]) ],
                        [ copy(old_mountain_road[2]),
                          copy(old_mountain_road[3]),
                          copy(old_mountain_road[4]) ],
                        [ copy(old_mountain_road[5]),
                          copy(old_mountain_road[6]),
                          copy(old_mountain_road[7]) ] ]

    result = list(SplitCollectionsOnTag(tag='highway', group=highway_roads).process(data))

    assert(result == expected_result)
    assert(len(result) == 3)
    assert(len(result[0]) == 2)
    assert(len(result[1]) == 3)
    assert(len(result[2]) == 3)

def test_no_surface_tag_paved_group(raymond_road, surfaces_paved):
    data = [raymond_road]
    expected_result = [copy(raymond_road)]

    result = list(SplitCollectionsOnTag(tag='surface', group=surfaces_paved).process(data))

    assert(result == expected_result)
    assert(len(result) == 1)
    assert(len(result[0]) == 5)

def test_no_surface_tag_unpaved_group(raymond_road, surfaces_unpaved):
    data = [raymond_road]
    expected_result = [copy(raymond_road)]

    result = list(SplitCollectionsOnTag(tag='surface', group=surfaces_unpaved, exclude_ways_missing_tag=True).process(data))

    assert(result == expected_result)
    assert(len(result) == 1)
    assert(len(result[0]) == 5)

def test_alternating_paved_unpaved_with_paved_group(barnes_road, surfaces_paved):
    data = [barnes_road]
    expected_result = [ [ copy(barnes_road[0]) ],
                        [ copy(barnes_road[1]) ],
                        [ copy(barnes_road[2]),
                          copy(barnes_road[3]) ] ]

    result = list(SplitCollectionsOnTag(tag='surface', group=surfaces_paved).process(data))

    assert(result == expected_result)
    assert(len(result) == 3)
    assert(len(result[0]) == 1)
    assert(len(result[1]) == 1)
    assert(len(result[2]) == 2)

def test_alternating_paved_unpaved_with_unpaved_group(barnes_road, surfaces_unpaved):
    data = [barnes_road]
    expected_result = [ [ copy(barnes_road[0]) ],
                        [ copy(barnes_road[1]) ],
                        [ copy(barnes_road[2]),
                          copy(barnes_road[3]) ] ]

    result = list(SplitCollectionsOnTag(tag='surface', group=surfaces_unpaved, exclude_ways_missing_tag=True).process(data))

    assert(result == expected_result)
    assert(len(result) == 3)
    assert(len(result[0]) == 1)
    assert(len(result[1]) == 1)
    assert(len(result[2]) == 2)
