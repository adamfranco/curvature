# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from curvature.post_processors.roll_up_curvature import RollUpCurvature
import pytest

@pytest.fixture
def roads():
    return [
        {'join_type': 'arbitrary',
         'ways': [
            { 'id': 1,
                'segments': [
                    {'curvature': 2},
                    {'curvature': 4},
                    {'curvature': 5}]},
            {   'id': 2,
                'segments': [
                    {'curvature': 3},
                    {'curvature': 5},
                    {'curvature': 7}]}]},
        {'join_type': 'none',
         'ways': [
            { 'id': 3,
                'segments': [
                    {'curvature': 23},
                    {'curvature': 5},
                    {'curvature': 7}]}]}]

def test_add_curvature(roads):
    result = list(RollUpCurvature().process(roads))
    assert result[0]['ways'][0]['curvature'] == 11
    assert result[0]['ways'][1]['curvature'] == 15
    assert result[0]['curvature'] == 26
    assert result[1]['ways'][0]['curvature'] == 35
    assert result[1]['curvature'] == 35

def test_add_curvature_ways_only(roads):
    result = list(RollUpCurvature(True, False).process(roads))
    assert result[0]['ways'][0]['curvature'] == 11
    assert result[0]['ways'][1]['curvature'] == 15
    assert 'curvature' not in result[0]
    assert result[1]['ways'][0]['curvature'] == 35
    assert 'curvature' not in result[1]

def test_add_curvature_collections_only(roads):
    result = list(RollUpCurvature(False, True).process(roads))
    assert result[0]['curvature'] == 26
    assert 'curvature' not in result[0]['ways'][0]
    assert 'curvature' not in result[0]['ways'][1]
    assert result[1]['curvature'] == 35
    assert 'curvature' not in result[1]['ways'][0]
