from curvature.post_processors.filter_segments_by_radius import FilterSegmentsByRadius

def test_filter_radius_min():
    first = {
        'start': [1,1],
        'radius': 2,
        'end': [2,2]
    }
    second = {
        'start': [2,2],
        'radius': 4,
        'end': [3,3]
    }
    third = {
        'start': [3,3],
        'radius': 5,
        'end': [4,4]
    }
    fourth = {
        'start': [4,4],
        'radius': 1,
        'end': [5,5]
    }
    item = {
        'segments':
        [
            first,
            second,
            third,
            fourth,
        ]
    }
    data = [[item]]
    result = list(FilterSegmentsByRadius(min=5).process(data))
    result_item = result[0][0]
    assert([entry['radius'] for entry in result_item['segments']] == [2, 5, 1])
    assert(first['end'] == third['start'])

def test_filter_radius_max():
    first = {
        'start': [1,1],
        'radius': 2,
        'end': [2,2]
    }
    second = {
        'start': [2,2],
        'radius': 4,
        'end': [3,3]
    }
    third = {
        'start': [3,3],
        'radius': 5,
        'end': [4,4]
    }
    fourth = {
        'start': [4,4],
        'radius': 1,
        'end': [5,5]
    }
    item = {
        'segments':
        [
            first,
            second,
            third,
            fourth,
        ]
    }
    data = [[item]]
    result = list(FilterSegmentsByRadius(max=4).process(data))
    result_item = result[0][0]
    assert([entry['radius'] for entry in result_item['segments']] == [2, 4, 1])
    assert(second['end'] == fourth['start'])
