# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature
from curvature.post_processors.head import Head
def test_chaining_post_processors():
    head = Head(num=1)
    filter_collections_by_curvature = FilterCollectionsByCurvature(min=5)
    data = [
        {'join_type': 'none',
         'ways': [
            {   'id': 1,
                'curvature': 2,
                'segments': [ {'curvature': 2}]}]},
        {'join_type': 'none',
         'ways': [
            {   'id': 2,
                'segments': [   {'curvature': 2},
                                {'curvature': 3}]}]},
        {'join_type': 'none',
         'ways': [
            {  'id': 3,
                'curvature': 6,
                'segments': [   {'curvature': 3},
                                {'curvature': 3}]}]},
    ]
    chain = reduce(lambda acc, processor: processor.process(acc), [data, filter_collections_by_curvature, head])
    result = list(chain)
    assert len(result) == 1, "Only 1 road should have matched."
    assert result[0]['ways'][0]['id'] == 2, "Road #1 should be in the result set."
