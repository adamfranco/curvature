# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from curvature.match import And
from curvature.match import Or
from curvature.match import Not
from curvature.match import TagEmpty
from curvature.match import TagEquals

@pytest.fixture
def way_residential_no():
    return {   'id': '100000',
        'tags': {
            'highway': 'residential',
            'tiger:reviewed': 'no'}}

@pytest.fixture
def way_residential_yes():
    return {
        'id': '100001',
        'tags': {
            'highway': 'residential',
            'tiger:reviewed': 'yes'}}

@pytest.fixture
def way_residential():
    return {
        'id': '100002',
        'tags': {
            'highway': 'residential'}}

@pytest.fixture
def way_unclassified():
    return {
        'id': '100003',
        'tags': {
            'highway': 'unclassified'}}

@pytest.fixture
def way_unclassified_no():
    return {
        'id': '100002',
        'tags': {
            'highway': 'unclassified',
            'tiger:reviewed': 'no'}}

@pytest.fixture
def collection_1(way_residential_no, way_residential_yes, way_residential, way_unclassified):
    return {
        'join_type': 'arbitrary',
        'ways': [
            way_residential_no,
            way_residential_yes,
            way_residential,
            way_unclassified
        ]}

@pytest.fixture
def collection_2(way_unclassified):
    return {
        'join_type': 'none',
        'ways': [
            way_unclassified
        ]}

@pytest.fixture
def collection_3(way_residential_no):
    return {
        'join_type': 'none',
        'ways': [
            way_residential_no
        ]}

@pytest.fixture
def collection_4(way_residential):
    return {
        'join_type': 'none',
        'ways': [
            way_residential
        ]}

def test_tag_equals(collection_1, collection_2, way_residential, way_unclassified):
    residential = TagEquals('highway', 'residential')
    assert residential.match_way(way_residential)
    assert not residential.match_way(way_unclassified)
    assert residential.match_collection(collection_1)
    assert residential.match(way_residential)
    assert not residential.match(way_unclassified)
    assert residential.match(collection_1)
    assert not residential.match(collection_2)

def test_tag_empty(collection_1, collection_2, collection_3, way_residential, way_residential_no):
    empty = TagEmpty('tiger:reviewed')
    assert not empty.match_way(way_residential_no)
    assert empty.match_way(way_residential)
    assert empty.match_collection(collection_1)
    assert empty.match(way_residential)
    assert not empty.match(way_residential_no)
    assert empty.match(collection_1)
    assert empty.match(collection_2)
    assert not empty.match(collection_3)

def test_and_ways(way_residential_no, way_residential, way_unclassified, way_unclassified_no):
    both = And(TagEquals('highway', 'residential'), TagEmpty('tiger:reviewed'))
    assert both.match(way_residential)
    assert not both.match(way_residential_no)

    both = And(TagEquals('highway', 'residential'), TagEquals('tiger:reviewed', 'no'))
    assert both.match(way_residential_no)
    assert not both.match(way_residential)
    assert not both.match(way_unclassified_no)

def test_and_collections(collection_1, collection_2, collection_3, collection_4):
    both = And(TagEquals('highway', 'residential'), TagEmpty('tiger:reviewed'))
    assert both.match(collection_1)
    assert not both.match(collection_2)
    assert not both.match(collection_3)
    assert both.match(collection_4)

def test_or(way_residential_no, way_residential, way_unclassified, way_unclassified_no):
    both = Or(TagEquals('highway', 'residential'), TagEmpty('tiger:reviewed'))
    assert both.match(way_residential)
    assert both.match(way_residential_no)
    assert both.match(way_unclassified)
    assert not both.match(way_unclassified_no)

def test_or_collections(collection_1, collection_2, collection_3, collection_4):
    both = Or(TagEquals('highway', 'residential'), TagEmpty('tiger:reviewed'))
    assert both.match(collection_1)
    assert both.match(collection_2)
    assert both.match(collection_3)
    assert both.match(collection_4)

    both = Or(TagEquals('highway', 'residential'), TagEquals('tiger:reviewed', 'no'))
    assert both.match(collection_1)
    assert not both.match(collection_2)
    assert both.match(collection_3)
    assert both.match(collection_4)

def test_not(collection_2, way_unclassified, way_residential):
    not_residential = Not(TagEquals('highway', 'residential'))
    assert not_residential.match(way_unclassified)
    assert not not_residential.match(way_residential)
    assert not_residential.match(collection_2)
