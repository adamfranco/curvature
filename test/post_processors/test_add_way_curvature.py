from curvature.post_processors.add_way_curvature import AddWayCurvature

def test_add_curvature():
    roads = [[{ 'id': 1,
                'segments': [
                    {'curvature': 2},
                    {'curvature': 4},
                    {'curvature': 5}]},
            {   'id': 2,
                'segments': [
                    {'curvature': 3},
                    {'curvature': 5},
                    {'curvature': 7}]}],
            [{ 'id': 3,
                'segments': [
                    {'curvature': 23},
                    {'curvature': 5},
                    {'curvature': 7}]}]]
    result = list(AddWayCurvature().process(roads))
    assert result[0][0]['curvature'] == 11
    assert result[0][1]['curvature'] == 15
    assert result[1][0]['curvature'] == 35
