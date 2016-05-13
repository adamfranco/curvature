import pytest
from curvature.post_processors.filter_collections_by_num_ways import FilterCollectionsByNumWays

@pytest.fixture
def roads():
    return [
        [{'id': 1}],
        [{'id': 2}, {'id': 3}],
        [{'id': 4}, {'id': 5}, {'id': 6}]
    ]

def test_filter_collections_by_num_ways_min(roads):
    result = list(FilterCollectionsByNumWays(min=2).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert len(result[0]) == 2, "The pair of ways should be in the result set."
    assert len(result[1]) == 3, "The trio of ways should be in the result set."


def test_filter_collections_by_num_ways_max(roads):
    result = list(FilterCollectionsByNumWays(max=2).process(roads))
    assert len(result) == 2, "Only 2 roads should have matched."
    assert len(result[0]) == 1, "The single way should be in the result set."
    assert len(result[1]) == 2, "The pair of ways should be in the result set."


def test_filter_collections_by_num_ways_min_max(roads):
    result = list(FilterCollectionsByNumWays(min=2, max=2).process(roads))
    assert len(result) == 1, "Only 1 road should have matched."
    assert len(result[0]) == 2, "The pair of ways should be in the result set."
