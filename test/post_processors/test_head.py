# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from curvature.post_processors.head import Head

def test_head():
    first = {
        'join_type': 'none',
        'ways': [{'length': 7}]
    }
    second = {
        'join_type': 'none',
        'ways': [{'length': 4}]
    }
    third = {
        'join_type': 'none',
        'ways': [{'length': 5}]
    }
    data = [
        first,
        second,
        third,
    ]
    result = list(Head(num=2).process(data))
    assert(len(result) == 2)
