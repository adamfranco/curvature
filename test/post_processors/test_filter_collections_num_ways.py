import pytest
from curvature.post_processors.filter_collections_by_num_ways import FilterCollectionsByNumWays

@pytest.fixture
def roads():
    return [
        {'join_type': 'none', 'ways': [{'id': 1}]},
        {'join_type': 'arbitrary', 'ways': [{'id': 2}, {'id': 3}]},
        {'join_type': 'arbitrary', 'ways': [{'id': 4}, {'id': 5}, {'id': 6}]}
    ]

def test_filter_collections_by_num_ways_min(roads):
    result = list(FilterCollectionsByNumWays(min=2).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert len(result[0]['ways']) == 2, "The pair of ways should be in the result set."
    assert len(result[1]['ways']) == 3, "The trio of ways should be in the result set."


def test_filter_collections_by_num_ways_max(roads):
    result = list(FilterCollectionsByNumWays(max=2).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert len(result[0]['ways']) == 1, "The single way should be in the result set."
    assert len(result[1]['ways']) == 2, "The pair of ways should be in the result set."


def test_filter_collections_by_num_ways_min_max(roads):
    result = list(FilterCollectionsByNumWays(min=2, max=2).process(roads))
    assert len(result) == 1, "Only 1 road should have matched."
    assert len(result[0]['ways']) == 2, "The pair of ways should be in the result set."
