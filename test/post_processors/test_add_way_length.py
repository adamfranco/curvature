from curvature.post_processors.add_way_length import AddWayLength

def test_add_length():
    roads = [
        {'join_type': 'arbitrary',
         'ways': [
            { 'id': 1,
                'segments': [
                    {'length': 2},
                    {'length': 4},
                    {'length': 5}]},
            {   'id': 2,
                'segments': [
                    {'length': 3},
                    {'length': 5},
                    {'length': 7}]}]},
        {'join_type': 'none',
         'ways': [
            { 'id': 3,
                'segments': [
                    {'length': 23},
                    {'length': 5},
                    {'length': 7}]}]}]
    result = list(AddWayLength().process(roads))
    assert result[0]['ways'][0]['length'] == 11
    assert result[0]['ways'][1]['length'] == 15
    assert result[1]['ways'][0]['length'] == 35
