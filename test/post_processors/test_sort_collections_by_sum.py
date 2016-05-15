import pytest
from curvature.post_processors.sort_collections_by_sum import SortCollectionsBySum

@pytest.fixture
def roads():
    return [
        [   {   'id': 1,
                'segments': [ {'length': 3}]},
            {   'id': 2,
                'length': 7,
                'segments': [ {'length': 7}]}],
        [   {   'id': 3,
                'segments': [   {'length': 2},
                                {'length': 2}]}],
        [   {   'id': 4,
                'length': 7,
                'segments': [   {'length': 3},
                                {'length': 4}]}],
    ]

def test_sort_collections_by_sum_desc(roads):
    result = list(SortCollectionsBySum(key='length', reverse=True).process(roads))
    assert len(result) == 3, "We should still have 3 collections"
    assert result[0][0]['id'] == 1
    assert result[0][1]['id'] == 2
    assert result[1][0]['id'] == 4
    assert result[2][0]['id'] == 3


def test_sort_collections_by_sum_asc(roads):
    result = list(SortCollectionsBySum(key='length').process(roads))
    assert len(result) == 3, "We should still have 3 collections"
    assert result[0][0]['id'] == 3
    assert result[1][0]['id'] == 4
    assert result[2][0]['id'] == 1
    assert result[2][1]['id'] == 2
