# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from copy import copy
from curvature.collector import WayCollector

class MockOSMParser(object):

    nodes_callback = None
    ways_callback = None
    relations_callback = None
    coords_callback = None

    def __init__(self, concurrency=None, nodes_callback=None, ways_callback=None,
            relations_callback=None, coords_callback=None, nodes_tag_filter=None,
            ways_tag_filter=None, relations_tag_filter=None, marshal_elem_data=False):
        if nodes_callback:
            self.nodes_callback = nodes_callback
        if ways_callback:
            self.ways_callback = ways_callback
        if relations_callback:
            self.relations_callback = relations_callback
        if coords_callback:
            self.coords_callback = coords_callback

    def parse(self, filename):
        if self.nodes_callback:
            self.nodes_callback(self.nodes())
        if self.ways_callback:
            self.ways_callback(self.ways())
        if self.relations_callback:
            self.relations_callback(self.relations())
        if self.coords_callback:
            self.coords_callback(self.coords())

class RoadAParser(MockOSMParser):

    def ways(self):
        return [
            (
                10000,
                {   'name':     'Road A',
                    'highway':  'unclassified'},
                [15, 16, 17, 18]
            ),
            # Can be appended in normal order
            (
                10001,
                {   'name':     'Road A',
                    'highway':  'unclassified'},
                [18, 19, 20, 21]
            ),
            # Can be appended in reverse order
            (
                10002,
                {   'name':     'Road A',
                    'highway':  'unclassified'},
                [24, 23, 22, 21]
            ),
            # Can be pre-pended in normal order
            (
                10003,
                {   'name':     'Road A',
                    'highway':  'unclassified'},
                [12, 13, 14, 15]
            ),
            # Can be pre-pended in reverse order
            (
                10004,
                {   'name':     'Road A',
                    'highway':  'unclassified'},
                [12, 11, 10, 9]
            ),
        ]

    def coords(self):
        return [
            (9, 43.70009, -73.00009),
            (10, 43.70010, -73.00010),
            (11, 43.70011, -73.00011),
            (12, 43.70012, -73.00012),
            (13, 43.70013, -73.00013),
            (14, 43.70014, -73.00014),
            (15, 43.70015, -73.00015),
            (16, 43.70016, -73.00016),
            (17, 43.70017, -73.00017),
            (18, 43.70018, -73.00018),
            (19, 43.70019, -73.00019),
            (20, 43.70020, -73.00020),
            (21, 43.70021, -73.00021),
            (22, 43.70022, -73.00022),
            (23, 43.70023, -73.00023),
            (24, 43.70024, -73.00024)
        ]

class Vermont125Parser(MockOSMParser):

    def ways(self):
        return [
            (
                20000,
                {   'name':     'South Main Street',
                    'ref':      'VT 125',
                    'highway':  'secondary'},
                [215, 216, 217, 218]
            ),
            # Can be appended in normal order
            (
                20001,
                {   'name':     'Court Street',
                    'ref':      'US 7;VT 125',
                    'highway':  'primary'},
                [218, 219, 220, 221]
            ),
            # Can be appended in reverse order
            (
                20002,
                {   'name':     'Main Street',
                    'ref':      'VT 125;VT 30',
                    'highway':  'secondary'},
                [224, 223, 222, 221]
            ),
            # Can be pre-pended in normal order
            (
                20003,
                {   'name':     'Ripton Road',
                    'ref':      'VT 125',
                    'highway':  'secondary'},
                [212, 213, 214, 215]
            ),
            # Can be pre-pended in reverse order
            (
                20004,
                {   'name':     'Hancock Road',
                    'ref':      'VT 125',
                    'highway':  'secondary'},
                [212, 211, 210, 209]
            ),
        ]

    def coords(self):
        return [
            (209, 43.70009, -73.00009),
            (210, 43.70010, -73.00010),
            (211, 43.70011, -73.00011),
            (212, 43.70012, -73.00012),
            (213, 43.70013, -73.00013),
            (214, 43.70014, -73.00014),
            (215, 43.70015, -73.00015),
            (216, 43.70016, -73.00016),
            (217, 43.70017, -73.00017),
            (218, 43.70018, -73.00018),
            (219, 43.70019, -73.00019),
            (220, 43.70020, -73.00020),
            (221, 43.70021, -73.00021),
            (222, 43.70022, -73.00022),
            (223, 43.70023, -73.00023),
            (224, 43.70024, -73.00024)
        ]

class Vermont125AndUs7Parser(Vermont125Parser):

    def ways(self):
        ways = super(Vermont125AndUs7Parser, self).ways()
        # Add a segment from US 7 that will be joined.
        ways.append((
                30001,
                {   'name':     'North Pleasant Street',
                    'ref':      'US 7',
                    'highway':  'primary'},
                [301, 221]
            ))

        # Add a disconnected segment from US 7 that won't be joined.
        ways.append((
                30002,
                {   'name':     'Ethan Allen Highway',
                    'ref':      'US 7',
                    'highway':  'primary'},
                [325, 326]
            ))
        return ways

    def coords(self):
        coords = super(Vermont125AndUs7Parser, self).coords()
        coords.append((301, 43.70301, -73.00301))
        coords.append((325, 43.70325, -73.00325))
        coords.append((326, 43.70326, -73.00326))
        return coords


def test_collector_road_a():
    collector = WayCollector(parser_class=RoadAParser)
    collections = []
    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))
    assert len(collections) == 1
    assert len(collections[0]['ways']) == 5
    assert collections[0]['join_type'] == 'name'
    assert collections[0]['join_data'] == 'Road A'

    expected_asc= [{'coords': [(-73.00009, 43.70009),
                          (-73.0001, 43.7001),
                          (-73.00011, 43.70011),
                          (-73.00012, 43.70012)],
               'id': 10004,
               'refs': [9, 10, 11, 12],
               'tags': {'highway': 'unclassified', 'name': 'Road A'}},
              {'coords': [(-73.00012, 43.70012),
                          (-73.00013, 43.70013),
                          (-73.00014, 43.70014),
                          (-73.00015, 43.70015)],
               'id': 10003,
               'refs': [12, 13, 14, 15],
               'tags': {'highway': 'unclassified', 'name': 'Road A'}},
              {'coords': [(-73.00015, 43.70015),
                          (-73.00016, 43.70016),
                          (-73.00017, 43.70017),
                          (-73.00018, 43.70018)],
               'id': 10000,
               'refs': [15, 16, 17, 18],
               'tags': {'highway': 'unclassified', 'name': 'Road A'}},
              {'coords': [(-73.00018, 43.70018),
                          (-73.00019, 43.70019),
                          (-73.0002, 43.7002),
                          (-73.00021, 43.70021)],
               'id': 10001,
               'refs': [18, 19, 20, 21],
               'tags': {'highway': 'unclassified', 'name': 'Road A'}},
              {'coords': [(-73.00021, 43.70021),
                          (-73.00022, 43.70022),
                          (-73.00023, 43.70023),
                          (-73.00024, 43.70024)],
                'id': 10002,
                'refs': [21, 22, 23, 24],
                'tags': {'highway': 'unclassified', 'name': 'Road A'}}
        ]
    # Joining happened in ascending order.
    if collections[0]['ways'][0]['id'] == expected_asc[0]['id']:
        assert collections[0]['ways'] == expected_asc, "If joined in ascending order, collection must match."
    # joining happened in descending order
    else:
        assert collections[0]['ways'] == reverse(expected_asc), "If joined in descending order, collection must match."

def test_collector_ref_matching():
    collector = WayCollector(parser_class=Vermont125Parser)
    collections = []

    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))
    assert len(collections) == 3 # VT 30, VT 125, US 7
    # Get the collection for VT 125.
    found = False
    for collection in collections:
        if collection['join_type'] == 'ref' and collection['join_data'] == 'VT 125':
            found = True
            break
    assert len(collection['ways']) == 5
    assert collection['join_type'] == 'ref'
    assert collection['join_data'] == 'VT 125'

    expected_asc= [{'coords': [(-73.00009, 43.70009),
                          (-73.0001, 43.7001),
                          (-73.00011, 43.70011),
                          (-73.00012, 43.70012)],
               'id': 20004,
               'refs': [209, 210, 211, 212],
               'tags': {'highway': 'secondary', 'name': 'Hancock Road', 'ref': 'VT 125'}},
              {'coords': [(-73.00012, 43.70012),
                          (-73.00013, 43.70013),
                          (-73.00014, 43.70014),
                          (-73.00015, 43.70015)],
               'id': 20003,
               'refs': [212, 213, 214, 215],
               'tags': {'highway': 'secondary', 'name': 'Ripton Road', 'ref': 'VT 125'}},
              {'coords': [(-73.00015, 43.70015),
                          (-73.00016, 43.70016),
                          (-73.00017, 43.70017),
                          (-73.00018, 43.70018)],
               'id': 20000,
               'refs': [215, 216, 217, 218],
               'tags': {'highway': 'secondary', 'name': 'South Main Street', 'ref': 'VT 125'}},
              {'coords': [(-73.00018, 43.70018),
                          (-73.00019, 43.70019),
                          (-73.0002, 43.7002),
                          (-73.00021, 43.70021)],
               'id': 20001,
               'refs': [218, 219, 220, 221],
               'tags': {'highway': 'primary', 'name': 'Court Street', 'ref': 'US 7;VT 125'}},
              {'coords': [(-73.00021, 43.70021),
                          (-73.00022, 43.70022),
                          (-73.00023, 43.70023),
                          (-73.00024, 43.70024)],
                'id': 20002,
                'refs': [221, 222, 223, 224],
                'tags': {'highway': 'secondary', 'name': 'Main Street', 'ref': 'VT 125;VT 30'}}
        ]
    # Joining happened in ascending order.
    if collection['ways'][0]['id'] == expected_asc[0]['id']:
        assert collection['ways'] == expected_asc, "If joined in ascending order, collection must match."
    # joining happened in descending order
    else:
        assert collection['ways'] == reverse(expected_asc), "If joined in descending order, collection must match."

# This test validates that ways that are part of a route won't be dropped if they
# can't be joined to other ways in that route as part of a collection. Instead
# they will just form their own collection.
def test_collector_doesnt_drop_unjoined_ways():
    collector = WayCollector(parser_class=Vermont125AndUs7Parser)
    collections = []

    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))
    assert len(collections) == 4 # VT 30, VT 125, two for US 7

    # First collection, could not be joined to the others since it has no refs in common.
    assert collections[2]['join_type'] == 'ref'
    assert collections[2]['join_data'] == 'US 7'
    assert len(collections[2]['ways']) == 1
    assert collections[2]['ways'][0]['id'] == 30002

    # Second collection, could be joined to the others
    assert collections[3]['join_type'] == 'ref'
    assert collections[3]['join_data'] == 'US 7'
    assert len(collections[3]['ways']) == 2
    assert collections[3]['ways'][0]['id'] == 20001
    assert collections[3]['ways'][1]['id'] == 30001


# Reverse an array of ways.
# This will allow tests to remain valid even if the logic changes for join order,
# since it is a totally valid result to join ways in either order.
def reverse(ways):
    reversed = copy(ways)
    reversed.reverse()
    for way in reversed:
        way['refs'].reverse()
        way['coords'].reverse()
    return reversed
