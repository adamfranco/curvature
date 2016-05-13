from curvature.post_processors.remove_way_properties import RemoveWayProperties

def test_remove_fields():
    data = [[
        {   'id': 1234,
            'curvature': 3,
            'length': 5,
            'refs': [1, 2, 3, 4],
            'tags': {   'name': 'foo',
                        'highway': 'unclassified'}},
        {   'id': 5678,
            'curvature': 3,
            'length': 5,
            'refs': [5, 6, 7, 8],
            'tags': {   'name': 'foo',
                        'highway': 'unclassified'}}]]

    result = list(RemoveWayProperties(properties=['length', 'refs']).process(data))

    expected = [[
        {   'id': 1234,
            'curvature': 3,
            'tags': {   'name': 'foo',
                        'highway': 'unclassified'}},
        {   'id': 5678,
            'curvature': 3,
            'tags': {   'name': 'foo',
                        'highway': 'unclassified'}}]]

    assert(result == expected)
