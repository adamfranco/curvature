# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from curvature.post_processors.roll_up_length import RollUpLength
import pytest

@pytest.fixture
def roads():
    return [
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

def test_add_length(roads):
    result = list(RollUpLength().process(roads))
    assert result[0]['ways'][0]['length'] == 11
    assert result[0]['ways'][1]['length'] == 15
    assert result[0]['length'] == 26
    assert result[1]['ways'][0]['length'] == 35
    assert result[1]['length'] == 35

def test_add_length_ways_only(roads):
    result = list(RollUpLength(True, False).process(roads))
    assert result[0]['ways'][0]['length'] == 11
    assert result[0]['ways'][1]['length'] == 15
    assert 'length' not in result[0]
    assert result[1]['ways'][0]['length'] == 35
    assert 'length' not in result[1]

def test_add_length_collections_only(roads):
    result = list(RollUpLength(False, True).process(roads))
    assert result[0]['length'] == 26
    assert 'length' not in result[0]['ways'][0]
    assert 'length' not in result[0]['ways'][1]
    assert result[1]['length'] == 35
    assert 'length' not in result[1]['ways'][0]
