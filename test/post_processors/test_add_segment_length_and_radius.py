# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from curvature.post_processors.add_segment_length_and_radius import AddSegmentLengthAndRadius
from copy import copy

@pytest.fixture
def south_union_street(south_union_street_a, south_union_street_b):
    return {'join_type': 'name', 'ways': [south_union_street_a, south_union_street_b]}

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
                    [44.47728820000014, -73.20902659999983]],
                'segments': [
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
                        'end':    [44.47728820000014, -73.20902659999983]}]
            }

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
                    [44.48055300000012, -73.20930960000047]],
                'segments': [
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
                        'end':    [44.48055300000012, -73.20930960000047]}]
            }

@pytest.fixture
def basic_straight_road():
    return {
        'segments': [
            {
                'start': [0, 0],
                'end': [1, 0],
            },
            {
                'start': [1, 0],
                'end': [2, 0],
            },
            {
                'start': [2, 0],
                'end': [3, 0],
            },
            {
                'start': [3, 0],
                'end': [4, 0],
            },
        ]
    }

@pytest.fixture
def basic_curved_road():
    return {
        'segments': [
            {
                'start': [0.000, 0.000],
                'end': [0.001, 0.000],
            },
            {
                'start': [0.001, 0.000],
                'end': [0.002, 0.000],
            },
            {
                'start': [0.002, 0.000],
                'end': [0.003, 0.001],
            },
            {
                'start': [0.003, 0.001],
                'end': [0.003, 0.002],
            },
            {
                'start': [0.003, 0.002],
                'end': [0.003, 0.003],
            },
            {
                'start': [0.003, 0.003],
                'end': [0.003, 0.004],
            },
        ]
    }

def test_straight_road(basic_straight_road):
    data = [{'ways': [basic_straight_road]}]
    result = list(AddSegmentLengthAndRadius().process(data))
    segments = result[0]['ways'][0]['segments']
    # [{'end': [1, 0],
    #   'length': 111229.83322958752,
    #   'radius': 145159487741.38614,
    #   'start': [0, 0]},
    #  {'end': [2, 0],
    #   'length': 111229.83322958752,
    #   'radius': 96897816892.49901,
    #   'start': [1, 0]},
    #  {'end': [3, 0],
    #   'length': 111229.83322958752,
    #   'radius': 96897816892.49901,
    #   'start': [2, 0]},
    #  {'end': [4, 0],
    #   'length': 111229.83322962806,
    #   'radius': 10000,
    #   'start': [3, 0]}]
    assert(111229 <= segments[0]['length'] <= 111230)
    assert(111229 <= segments[1]['length'] <= 111230)
    assert(111229 <= segments[2]['length'] <= 111230)
    assert(111229 <= segments[3]['length'] <= 111230)
    assert(145159487741 <= segments[0]['radius'] < 145159487742)
    assert(96897816892 <= segments[1]['radius'] < 96897816893)
    assert(96897816892 <= segments[2]['radius'] < 96897816893)
    assert(10000 == segments[3]['radius'])

def test_curved_road(basic_curved_road):
    data = [{'ways': [basic_curved_road]}]
    result = list(AddSegmentLengthAndRadius().process(data))
    segments = result[0]['ways'][0]['segments']
    # [{'end': [0.001, 0.0],
    #   'length': 111.22983735621419,
    #   'radius': 6373000.524647183,
    #   'start': [0.0, 0.0]},
    #  {'end': [0.002, 0.0],
    #   'length': 111.22983735621419,
    #   'radius': 175.8698149547354,
    #   'start': [0.001, 0.0]},
    #  {'end': [0.003, 0.001],
    #   'length': 157.30274453170819,
    #   'radius': 175.8698149547354,
    #   'start': [0.002, 0.0]},
    #  {'end': [0.003, 0.002],
    #   'length': 111.22983735621419,
    #   'radius': 175.8698149547354,
    #   'start': [0.003, 0.001]},
    #  {'end': [0.003, 0.003],
    #   'length': 111.22983735621419,
    #   'radius': 6373000.524647183,
    #   'start': [0.003, 0.002]},
    #  {'end': [0.003, 0.004],
    #   'length': 111.22983735621419,
    #   'radius': 10000,
    #   'start': [0.003, 0.003]}]
    assert(111 <= segments[0]['length'] <= 112)
    assert(111 <= segments[1]['length'] <= 112)
    assert(157 <= segments[2]['length'] <= 158)
    assert(111 <= segments[3]['length'] <= 112)
    assert(111 <= segments[4]['length'] <= 112)
    assert(111 <= segments[5]['length'] <= 112)
    assert(6373000 <= segments[0]['radius'] <= 6373001)
    assert(175 <= segments[1]['radius'] <= 176)
    assert(175 <= segments[2]['radius'] <= 176)
    assert(175 <= segments[3]['radius'] <= 176)
    assert(6373000 <= segments[4]['radius'] <= 6373001)
    assert(10000 == segments[5]['radius'])

def test_add_to_a(south_union_street_a):
    data = [{'ways': [south_union_street_a]}]

    result = list(AddSegmentLengthAndRadius().process(data))
    segments = result[0]['ways'][0]['segments']

    # [{'end': [44.47606690000014, -73.20894139999983],
    #    'length': 133.9951171255431,
    #    'radius': 9042.031019056063,
    #    'radius_b': 9042.031019056063,
    # 'start': [44.47486310000014, -73.20887729999983]},
    # {'end': [44.47617410000035, -73.20894919999994],
    #    'length': 11.939194299937851,
    #    'radius': 5911.150339265277,
    #    'radius_a': 9042.031019056063,
    #    'radius_b': 5911.150339265277,
    # 'start': [44.47606690000014, -73.20894139999983]},
    # {'end': [44.47721230000033, -73.20902129999995],
    #    'length': 115.62050685215769,
    #    'radius': 5911.150339265277,
    #    'radius_a': 5911.150339265277,
    #    'radius_b': 6051.348955391984,
    # 'start': [44.47617410000035, -73.20894919999994]},
    # {'end': [44.47728820000014, -73.20902659999983],
    #    'length': 8.45242742062934,
    #    'radius': 6051.348955391984,
    #    'radius_a': 6051.348955391984,
    #    'radius_b': 1000000,
    # 'start': [44.47721230000033, -73.20902129999995]}]

    assert(133 <= segments[0]['length'] <= 134)
    # Only one radius option for the first segment.
    assert(9042 <= segments[0]['radius'] <= 9043)

    assert(11 <= segments[1]['length'] <= 12)
    # Radius must be one of or between the radii of both triangles.
    assert(5911 <= segments[1]['radius'] <= 9043)

    assert(115 <= segments[2]['length'] <= 116)
    # Radius must be one of or between the radii of both triangles.
    assert(5911 <= segments[2]['radius'] <= 6052)

    assert(8 <= segments[3]['length'] <= 9)
    # Only one real radius option for the last segment.
    assert(6051 <= segments[3]['radius'] <= 6052)


def test_add_segments_to_both(south_union_street):
    data = [south_union_street]

    result = list(AddSegmentLengthAndRadius().process(data))

    segments_a = result[0]['ways'][0]['segments']
    # A
    # [{'end': [44.47606690000014, -73.20894139999983],
    #    'length': 133.9951171255431,
    #    'radius': 9042.031019056063,
    #    'radius_b': 9042.031019056063,
    # 'start': [44.47486310000014, -73.20887729999983]},
    # {'end': [44.47617410000035, -73.20894919999994],
    #    'length': 11.939194299937851,
    #    'radius': 5911.150339265277,
    #    'radius_a': 9042.031019056063,
    #    'radius_b': 5911.150339265277,
    # 'start': [44.47606690000014, -73.20894139999983]},
    # {'end': [44.47721230000033, -73.20902129999995],
    #    'length': 115.62050685215769,
    #    'radius': 5911.150339265277,
    #    'radius_a': 5911.150339265277,
    #    'radius_b': 6051.348955391984,
    # 'start': [44.47617410000035, -73.20894919999994]},
    # {'end': [44.47728820000014, -73.20902659999983],
    #    'length': 8.45242742062934,
    #    'radius': 1515.5261720076899,
    #    'radius_a': 6051.348955391984,
    #    'radius_b': 1515.5261720076899,
    # 'start': [44.47721230000033, -73.20902129999995]}]

    assert(133 <= segments_a[0]['length'] <= 134)
    # Only one radius option for the first segment.
    assert(9042 <= segments_a[0]['radius'] <= 9043)

    assert(11 <= segments_a[1]['length'] <= 12)
    # Radius must be one of or between the radii of both triangles.
    assert(5911 <= segments_a[1]['radius'] <= 9043)

    assert(115 <= segments_a[2]['length'] <= 116)
    # Radius must be one of or between the radii of both triangles.
    assert(5911 <= segments_a[2]['radius'] <= 6052)

    assert(8 <= segments_a[3]['length'] <= 9)
    # Radius must be one of or between the radii of both triangles.
    # This last segment of the first way should now be just in the middle of the sequence.
    assert(1515 <= segments_a[3]['radius'] <= 6052)

    segments_b = result[0]['ways'][1]['segments']
    # B
    # [{'end': [44.477370500000326, -73.20903419999996],
    #    'length': 9.17384496193589,
    #    'radius': 1515.5261720076899,
    #    'radius_a': 1515.5261720076899,
    #    'radius_b': 5087.529749503991,
    # 'start': [44.47728820000014, -73.20902659999983]},
    # {'end': [44.478012899999946, -73.20909320000007],
    #    'length': 71.60721208643298,
    #    'radius': 3090.4324585426625,
    #    'radius_a': 5087.529749503991,
    #    'radius_b': 3090.4324585426625,
    # 'start': [44.477370500000326, -73.20903419999996]},
    # {'end': [44.478329400000135, -73.20911439999983],
    #    'length': 35.24433665520804,
    #    'radius': 3090.4324585426625,
    #    'radius_a': 3090.4324585426625,
    #    'radius_b': 3561.7154012566457,
    # 'start': [44.478012899999946, -73.20909320000007]},
    # {'end': [44.47902100000032, -73.20917629999997],
    #    'length': 77.08323683693155,
    #    'radius': 3501.915505841466,
    #    'radius_a': 3561.7154012566457,
    #    'radius_b': 3501.915505841466,
    # 'start': [44.478329400000135, -73.20911439999983]},
    # {'end': [44.47909000000013, -73.20918349999984],
    #    'length': 7.69627545970476,
    #    'radius': 581.3853353525011,
    #    'radius_a': 3501.915505841466,
    #    'radius_b': 581.3853353525011,
    # 'start': [44.47902100000032, -73.20917629999997]},
    # {'end': [44.479153100000325, -73.20918889999996],
    #    'length': 7.031266303832327,
    #    'radius': 581.3853353525011,
    #    'radius_a': 581.3853353525011,
    #    'radius_b': 6604.033701293703,
    # 'start': [44.47909000000013, -73.20918349999984]},
    # {'end': [44.48046430000036, -73.20930199999994],
    #    'length': 146.1204640900716,
    #    'radius': 6604.033701293703,
    #    'radius_a': 6604.033701293703,
    #    'radius_b': 8312.821062879286,
    # 'start': [44.479153100000325, -73.20918889999996]},
    # {'end': [44.48055300000012, -73.20930960000047],
    #    'length': 9.884128953281145,
    #    'radius': 8312.821062879286,
    #    'radius_a': 8312.821062879286,
    #    'radius_b': 1000000,
    # 'start': [44.48046430000036, -73.20930199999994]}]

    assert(9 <= segments_b[0]['length'] <= 10)
    # Radius must be one of or between the radii of both triangles.
    # This first segment of the second way should now be just in the middle of the sequence.
    assert(1515 <= segments_b[0]['radius'] <= 5088)

    assert(71 <= segments_b[1]['length'] <= 72)
    # Radius must be one of or between the radii of both triangles.
    assert(3090 <= segments_b[1]['radius'] <= 5088)

    assert(35 <= segments_b[2]['length'] <= 36)
    # Radius must be one of or between the radii of both triangles.
    assert(3090 <= segments_b[2]['radius'] <= 3562)

    assert(77 <= segments_b[3]['length'] <= 78)
    # Radius must be one of or between the radii of both triangles.
    assert(3501 <= segments_b[3]['radius'] <= 3562)

    assert(7 <= segments_b[4]['length'] <= 8)
    # Radius must be one of or between the radii of both triangles.
    assert(581 <= segments_b[4]['radius'] <= 3502)

    assert(7 <= segments_b[5]['length'] <= 8)
    # Radius must be one of or between the radii of both triangles.
    assert(581 <= segments_b[5]['radius'] <= 6605)

    assert(146 <= segments_b[6]['length'] <= 147)
    # Radius must be one of or between the radii of both triangles.
    assert(6604 <= segments_b[6]['radius'] <= 8313)

    assert(9 <= segments_b[7]['length'] <= 10)
    # Only one real radius option for the last segment.
    assert(8312 <= segments_b[7]['radius'] <= 8313)
