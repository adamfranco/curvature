import pytest
from curvature.collector import WayCollector

class MockOSMParser(object):

    nodes_callback = None
    ways_callback = None
    relations_callback = None
    coords_callback = None

    nodes = []
    ways = []
    relations = []
    coords = []

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
            self.nodes_callback(self.nodes)
        if self.ways_callback:
            self.ways_callback(self.ways)
        if self.relations_callback:
            for relation in self.relations:
                self.relations_callback(relation)
        if self.coords_callback:
            self.coords_callback(self.coords)

class RoadAParser(MockOSMParser):

    ways = [
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

    coords = [
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

def test_collector_road_a():
    collector = WayCollector(parser_class=RoadAParser)
    collections = []
    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))
    assert len(collections) == 1
    assert len(collections[0]) == 5

    # Joining happened in ascending order.
    if collections[0][0]['id'] == 10004:
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
        assert collections[0] == expected_asc, "If joined in ascending order, collection must match."
    # joining happened in descending order
    else:
        expected_desc= [{'coords': [(-73.00024, 43.70024),
                                  (-73.00023, 43.70023),
                                  (-73.00022, 43.70022),
                                  (-73.00021, 43.70021)],
                       'id': 10002,
                       'refs': [24, 23, 22, 21],
                       'tags': {'highway': 'unclassified', 'name': 'Road A'}},
                      {'coords': [(-73.00021, 43.70021),
                                  (-73.0002, 43.7002),
                                  (-73.00019, 43.70019),
                                  (-73.00018, 43.70018)],
                       'id': 10001,
                       'refs': [21, 20, 19, 18],
                       'tags': {'highway': 'unclassified', 'name': 'Road A'}},
                      {'coords': [(-73.00018, 43.70018),
                                  (-73.00017, 43.70017),
                                  (-73.00016, 43.70016),
                                  (-73.00015, 43.70015)],
                       'id': 10000,
                       'refs': [18, 17, 16, 15],
                       'tags': {'highway': 'unclassified', 'name': 'Road A'}},
                      {'coords': [(-73.00015, 43.70015),
                                  (-73.00014, 43.70014),
                                  (-73.00013, 43.70013),
                                  (-73.00012, 43.70012)],
                       'id': 10003,
                       'refs': [15, 14, 13, 12],
                       'tags': {'highway': 'unclassified', 'name': 'Road A'}},
                      {'coords': [(-73.00012, 43.70012),
                                  (-73.00011, 43.70011),
                                  (-73.0001, 43.7001),
                                  (-73.00009, 43.70009)],
                       'id': 10004,
                       'refs': [12, 11, 10, 9],
                       'tags': {'highway': 'unclassified', 'name': 'Road A'}}]

        assert collections[0] == expected_desc, "If joined in descending order, collection must match."
