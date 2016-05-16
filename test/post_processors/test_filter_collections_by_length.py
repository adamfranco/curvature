import pytest
from curvature.post_processors.filter_collections_by_length import FilterCollectionsByLength

@pytest.fixture
def roads():
    return [
        {'join_type': 'none',
         'ways': [
            {   'id': 1,
                'length': 2,
                'segments': [ {'length': 2}]}]},
        {'join_type': 'none',
         'ways': [
            {   'id': 2,
                'segments': [   {'length': 2},
                                {'length': 3}]}]},
        {'join_type': 'none',
         'ways': [
            {   'id': 3,
                'length': 6,
                'segments': [   {'length': 3},
                                {'length': 3}]}]}
    ]

def test_filter_length_min(roads):
    result = list(FilterCollectionsByLength(min=5).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert result[0]['ways'][0]['id'] == 2, "Road #2 should be in the result set."
    assert result[1]['ways'][0]['id'] == 3, "Road #3 should be in the result set."


def test_filter_length_max(roads):
    result = list(FilterCollectionsByLength(max=5).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert result[0]['ways'][0]['id'] == 1, "Road #1 should be in the result set."
    assert result[1]['ways'][0]['id'] == 2, "Road #2 should be in the result set."


def test_filter_length_min_max(roads):
    result = list(FilterCollectionsByLength(min=5, max=5).process(roads))
    assert len(result) == 1, "Only 1 road should have matched."
    assert result[0]['ways'][0]['id'] == 2, "Road #1 should be in the result set."
