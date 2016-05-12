import pytest
from curvature.post_processors.add_segments import AddSegments

@pytest.fixture
def south_union_street():
    return [south_union_street_a(), south_union_street_b()]

@pytest.fixture
def south_union_street_a():
    return {    'id': 24494215,
                'tags': {   'highway': 'tertiary',
                    'name': 'South Union Street',
                    'oneway': 'yes',
                    'surface': 'asphalt'},
                'refs': [204491078, 204491085, 2801588482, 2801784606, 204491091],
                'coords': [   [44.47486310000014, -73.20887729999983],
                    [44.47606690000014, -73.20894139999983],
                    [44.47617410000035, -73.20894919999994],
                    [44.47721230000033, -73.20902129999995],
                    [44.47728820000014, -73.20902659999983]]
            }

@pytest.fixture
def expected_south_union_street_a_segments():
    return [
        # 1st to 2nd
        {   'start':  [44.47486310000014, -73.20887729999983],
            'end':    [44.47606690000014, -73.20894139999983]},
        # 2nd to 3rd
        {   'start':  [44.47606690000014, -73.20894139999983],
            'end':    [44.47617410000035, -73.20894919999994]},
        # 3rd to 4th
        {   'start':  [44.47617410000035, -73.20894919999994],
            'end':    [44.47721230000033, -73.20902129999995]},
        # 4th to 5th
        {   'start':  [44.47721230000033, -73.20902129999995],
            'end':    [44.47728820000014, -73.20902659999983]}
    ]

@pytest.fixture
def south_union_street_b():
    return {    'id': 32775263,
                'tags': {   'cycleway': 'lane',
                    'highway': 'tertiary',
                    'name': 'South Union Street',
                    'oneway': 'yes',
                    'surface': 'asphalt'},
                'refs': [   204491091,
                    2801784615,
                    1221533877,
                    204491097,
                    2801784643,
                    204491102,
                    2801784660,
                    2801548045,
                    204437223],
                'coords': [   [44.47728820000014, -73.20902659999983],
                    [44.477370500000326, -73.20903419999996],
                    [44.478012899999946, -73.20909320000007],
                    [44.478329400000135, -73.20911439999983],
                    [44.47902100000032, -73.20917629999997],
                    [44.47909000000013, -73.20918349999984],
                    [44.479153100000325, -73.20918889999996],
                    [44.48046430000036, -73.20930199999994],
                    [44.48055300000012, -73.20930960000047]]
            }

@pytest.fixture
def expected_south_union_street_b_segments():
    return [
        # 1st to 2nd
        {   'start':  [44.47728820000014, -73.20902659999983],
            'end':    [44.477370500000326, -73.20903419999996]},
        # 2nd to 3rd
        {   'start':  [44.477370500000326, -73.20903419999996],
            'end':    [44.478012899999946, -73.20909320000007]},
        # 3rd to 4th
        {   'start':  [44.478012899999946, -73.20909320000007],
            'end':    [44.478329400000135, -73.20911439999983]},
        # 4th to 5th
        {   'start':  [44.478329400000135, -73.20911439999983],
            'end':    [44.47902100000032, -73.20917629999997]},
        # 5th to 6th
        {   'start':  [44.47902100000032, -73.20917629999997],
            'end':    [44.47909000000013, -73.20918349999984]},
        # 6th to 7th
        {   'start':  [44.47909000000013, -73.20918349999984],
            'end':    [44.479153100000325, -73.20918889999996]},
        # 7rd to 8th
        {   'start':  [44.479153100000325, -73.20918889999996],
            'end':    [44.48046430000036, -73.20930199999994]},
        # 8th to 9th
        {   'start':  [44.48046430000036, -73.20930199999994],
            'end':    [44.48055300000012, -73.20930960000047]}
    ]

def test_add_segments_to_a(south_union_street_a, expected_south_union_street_a_segments):
    data = [[south_union_street_a]]

    result = list(AddSegments().process(data))

    assert(result[0][0]['segments'] == expected_south_union_street_a_segments)

def test_add_segments_to_both(south_union_street, expected_south_union_street_a_segments, expected_south_union_street_b_segments):
    data = [south_union_street]

    result = list(AddSegments().process(data))

    assert(result[0][0]['segments'] == expected_south_union_street_a_segments)
    assert(result[0][1]['segments'] == expected_south_union_street_b_segments)
