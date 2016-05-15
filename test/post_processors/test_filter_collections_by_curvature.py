import pytest
from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature

@pytest.fixture
def roads():
    return [
        [{  'id': 1,
            'curvature': 2,
            'segments': [ {'curvature': 2}]}],
        [{  'id': 2,
            'segments': [   {'curvature': 2},
                            {'curvature': 3}]}],
        [{  'id': 3,
            'curvature': 6,
            'segments': [   {'curvature': 3},
                            {'curvature': 3}]}],
    ]

def test_filter_collections_by_curvature_min(roads):
    result = list(FilterCollectionsByCurvature(min=5).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert result[0][0]['id'] == 2, "Road #2 should be in the result set."
    assert result[1][0]['id'] == 3, "Road #3 should be in the result set."


def test_filter_collections_by_curvature_max(roads):
    result = list(FilterCollectionsByCurvature(max=5).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert result[0][0]['id'] == 1, "Road #1 should be in the result set."
    assert result[1][0]['id'] == 2, "Road #2 should be in the result set."


def test_filter_collections_by_curvature_min_max(roads):
    result = list(FilterCollectionsByCurvature(min=5, max=5).process(roads))
    assert len(result) == 1, "Only 1 road should have matched."
    assert result[0][0]['id'] == 2, "Road #1 should be in the result set."
