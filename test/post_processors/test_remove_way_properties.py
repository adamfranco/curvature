# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from curvature.post_processors.remove_way_properties import RemoveWayProperties

def test_remove_fields():
    data = [
        {   'join_type': 'arbitrary',
            'ways': [
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
                                'highway': 'unclassified'}}]}]

    result = list(RemoveWayProperties(properties=['length', 'refs']).process(data))

    expected = [
        {   'join_type': 'arbitrary',
            'ways': [
                {   'id': 1234,
                    'curvature': 3,
                    'tags': {   'name': 'foo',
                                'highway': 'unclassified'}},
                {   'id': 5678,
                    'curvature': 3,
                    'tags': {   'name': 'foo',
                                'highway': 'unclassified'}}]}]

    assert(result == expected)
