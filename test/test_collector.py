# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
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

    expected = [{'coords': [(-73.00009, 43.70009),
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

    assert collections[0]['ways'] == expected

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

    expected = [{'coords': [(-73.00009, 43.70009),
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
    assert collection['ways'] == expected

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
    assert len(collections[2]['ways']) == 2
    assert collections[2]['ways'][0]['id'] == 20001
    assert collections[2]['ways'][1]['id'] == 30001

    # Second collection, could be joined to the others
    assert collections[3]['join_type'] == 'ref'
    assert collections[3]['join_data'] == 'US 7'
    assert len(collections[3]['ways']) == 1
    assert collections[3]['ways'][0]['id'] == 30002

# The following data is from the US 2 / US 302 junction in Montpelier, VT.
class US2Parser(MockOSMParser):

    def ways(self):
        return [
            (   158420755,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '1',
                    'name': 'River Street',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [1706151849, 1706151806, 205080612]),
            (   28483253,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '2',
                    'maxspeed': '35 mph',
                    'name': 'Berlin Street',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [   205006997,
                    205006999,
                    205007000,
                    # Ommitting intermediate points.
                    204983102,
                    205007012,
                    205007013,
                    205007014]),
            (   158420750,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '1',
                    'name': 'River Street',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [205080612, 1706151851, 1706151834]),
            (   172791608,
                {   'NHS': 'yes',
                    'highway': 'primary',
                    'junction': 'roundabout',
                    'lanes': '1',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [   1706151846,
                    1706151819,
                    1706151862,
                    1706151815,
                    1706151849]),
            (   172791605,
                {   'NHS': 'yes',
                    'highway': 'primary',
                    'junction': 'roundabout',
                    'lanes': '1',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [   1706151834,
                    1706151838,
                    1706151836,
                    1706151850,
                    1706151840,
                    1706151809,
                    1706151852,
                    1706151848,
                    1706151825,
                    1706151844]),
            (   158420754,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '1',
                    'name': 'River Street',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [1706151844, 1706151828, 1706151821, 205080585]),
            (   158420752,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '2',
                    'name': 'River Street',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [   205080585,
                    205080529,
                    205080587,
                    205080588,
                    # Ommitting intermediate points
                    205080646,
                    205080647,
                    205007035,
                    205006997]),
            (   143178266,
                {   'FIXME': 'check lanes',
                    'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '4',
                    'maxspeed': '50 mph',
                    'name': 'Memorial Drive',
                    'ref': 'US 2',
                    'surface': 'asphalt',
                    'tiger:cfcc': 'A41',
                    'tiger:county': 'Washington, VT',
                    'tiger:name_base': 'Memorial',
                    'tiger:name_type': 'Dr',
                    'tiger:reviewed': 'no'},
                [   205007014,
                    205059095,
                    205059094,
                    205059093,
                    # Ommitting intermediate points.
                    205059076,
                    205059075,
                    205059074,
                    204979640]),
            (   19724163,
                {   'highway': 'primary',
                    'name': 'Bailey Avenue',
                    'ref': 'US 2',
                    'surface': 'asphalt',
                    'tiger:cfcc': 'A41',
                    'tiger:county': 'Washington, VT',
                    'tiger:name_base': 'Bailey',
                    'tiger:name_type': 'Ave',
                    'tiger:reviewed': 'no',
                    'tiger:zip_left': '05602',
                    'tiger:zip_right': '05602'},
                [   204979640,
                    204979641,
                    534663608,
                    204979642,
                    # Ommitting intermediate points.
                    204968644,
                    204979646,
                    204979647,
                    204979648]),
            (   195936126,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '2',
                    'name': 'River Street',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [205080612, 205080611]),
            (   195936143,
                {   'NHS': 'yes',
                    'bridge': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '2',
                    'name': 'River Street',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [205080611, 205080608]),
            (   158420747,
                {   'NHS': 'yes',
                    'hgv': 'yes',
                    'highway': 'primary',
                    'lanes': '1',
                    'name': 'River Street',
                    'oneway': 'yes',
                    'ref': 'US 2',
                    'surface': 'asphalt'},
                [1706151846, 1706151827, 1706151817, 205080585])
        ]

    def coords(self):
        return [
            (1706151846, 44.24674290000081, -72.54948910000024),
            (1706151819, 44.2467102000008, -72.54942550000024),
            (1706151862, 44.24666550000081, -72.54938180000025),
            (1706151815, 44.2466248000008, -72.54936330000024),
            (1706151849, 44.24657070000082, -72.54936190000025),
            (1706151806, 44.2465015000008, -72.54929580000025),
            (205080612, 44.2463686000001, -72.54920230000006),
            (1706151851, 44.246405700000814, -72.54933900000026),
            (1706151834, 44.2464600000008, -72.54945710000025),
            (1706151838, 44.246440300000806, -72.54950970000026),
            (1706151836, 44.246432200000804, -72.54955290000025),
            (1706151850, 44.246433100000814, -72.54963300000026),
            (1706151840, 44.24644530000081, -72.54968570000025),
            (1706151809, 44.2464793000008, -72.54975330000025),
            (1706151852, 44.24651800000081, -72.54979270000025),
            (1706151848, 44.246566900000815, -72.54981590000025),
            (1706151825, 44.2466282000008, -72.54981440000024),
            (1706151844, 44.24668400000081, -72.54978250000025),
            (1706151828, 44.2468143000008, -72.54974990000025),
            (1706151821, 44.2468962000008, -72.54974280000025),
            (205080585, 44.24702170000011, -72.54974440000005),
            (205080529, 44.24712240000012, -72.54981020000004),
            (205080587, 44.24751400000011, -72.55020100000006),
            (205080588, 44.24782370000011, -72.55052100000006),
            (205080646, 44.25089700000013, -72.57016900000009),
            (205080647, 44.251056000000126, -72.57049200000009),
            (205007035, 44.2512519999998, -72.57085400000008),
            (205006997, 44.25151869999981, -72.57138020000012),
            (205006999, 44.251807999999805, -72.57162300000012),
            (205007000, 44.2526681999998, -72.57243690000011),
            (204983102, 44.256948999999906, -72.57693199999969),
            (205007012, 44.2572844999998, -72.57737410000011),
            (205007013, 44.257388199999795, -72.5775243000001),
            (205007014, 44.257586999999795, -72.5778090000001),
            (205059095, 44.257702999999886, -72.57795099999997),
            (205059094, 44.257809999999886, -72.57807299999997),
            (205059093, 44.257967999999885, -72.57822099999997),
            (205059076, 44.26018399999989, -72.58400799999998),
            (205059075, 44.26014899999989, -72.58429199999998),
            (205059074, 44.26009099999989, -72.58465399999997),
            (204979640, 44.260024999999814, -72.58498299999982),
            (204979641, 44.26009899999981, -72.58501699999982),
            (534663608, 44.260150499999824, -72.58504100000012),
            (204979642, 44.260291999999815, -72.58510699999982),
            (204968644, 44.26070500000007, -72.58522399999993),
            (204979646, 44.26080799999981, -72.58520899999984),
            (204979647, 44.26087799999981, -72.58519099999984),
            (204979648, 44.26107239999981, -72.58511829999983),
            (205080611, 44.246083700000106, -72.54889460000007),
            (205080608, 44.245636200000106, -72.54851690000007),
            (1706151846, 44.24674290000081, -72.54948910000024),
            (1706151827, 44.2468284000008, -72.54957810000025),
            (1706151817, 44.2469158000008, -72.54965480000024)
        ]

# This test validates that joining won't spiral back on itself in a roundabout.
def test_collector_joins_past_roundabout():
    collector = WayCollector(parser_class=US2Parser)
    collections = []

    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))

    assert collections[0]['ways'][8]['id'] == 19724163, "Low-id two-direction way. Should be base. Bailey Avenue"
    assert collections[0]['ways'][7]['id'] == 143178266, "2nd two-direction way. Memorial Drive."
    assert collections[0]['ways'][6]['id'] == 28483253, "3rd two-direction way. Berlin Street."
    assert collections[0]['ways'][5]['id'] == 158420752, "4th two-direction way. River Street."
    assert collections[0]['ways'][4]['id'] == 158420747, "Roundabout-exit, west-bound. River Street."
    assert collections[0]['ways'][3]['id'] == 172791608, "Roundabout, west-bound."
    assert collections[0]['ways'][2]['id'] == 158420755, "Roundabout-entrance, west-bound. River Street."
    assert collections[0]['ways'][1]['id'] == 195936126, "Two-direction way east of circle. River Street."
    assert collections[0]['ways'][0]['id'] == 195936143, "Two-direction way east of circle (bridge). River Street."

    assert collections[1]['ways'][0]['id'] == 158420750, "Roundabout-exit, east-bound. River Street."
    assert collections[1]['ways'][1]['id'] == 172791605, "Roundabout, east-bound."
    assert collections[1]['ways'][2]['id'] == 158420754, "Roundabout-entrance, east-bound. River Street."
    assert len(collections) == 2 # VT 30, VT 125, two for US 7


# The following data is from the CR 106 / Seven Lakes Drive junction in Stony Point, NY.
class CR106Parser(MockOSMParser):

    def ways(self):
        return [   (   20700007,
        {   'highway': 'tertiary',
            'name': 'County Road 106',
            'oneway': 'yes',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no',
            'tiger:zip_left': '10975',
            'tiger:zip_right': '10975'},
        [221933299, 222284381, 222284382]),
    (   31769423,
        {   'highway': 'secondary',
            'name': 'County Road 106',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no',
            'tiger:zip_left': '10975',
            'tiger:zip_right': '10975'},
        [   222284382,
            355635925,
            355635926,
            355635927,
            355635928,
            355635929,
            355635930,
            355635931]),
    (   241704628,
        {   'highway': 'tertiary',
            'name': 'County Road 106',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no'},
        [   222284291,
            222215697,
            222284295,
            222284299,
            222284303,
            222217173,
            222284306]),
    (   20700014,
        {   'highway': 'tertiary',
            'name': 'County Road 106',
            'oneway': 'yes',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no'},
        [222284306, 222284479, 222284482, 222284486, 221836401]),
    (   20700010,
        {   'highway': 'tertiary',
            'name': 'County Road 106',
            'oneway': 'yes',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no',
            'tiger:zip_left': '10975',
            'tiger:zip_right': '10975'},
        [222284382, 222284445, 222284448, 222284455, 221933290]),
    (   31769417,
        {   'highway': 'tertiary',
            'junction': 'roundabout',
            'oneway': 'yes',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no'},
        [   221933299,
            221933296,
            221933293,
            221933290,
            221836697,
            221836695,
            221836694,
            221836691,
            221836416,
            221836413,
            221836411,
            221836409,
            221836406,
            221836403,
            221836402,
            221836401,
            221836605,
            221933327,
            221933324,
            221933310,
            221933307,
            221933304,
            221933302,
            221933299]),
    (   31769426,
        {   'highway': 'tertiary',
            'name': 'County Road 106',
            'oneway': 'yes',
            'ref': 'CR 106',
            'tiger:cfcc': 'A41',
            'tiger:county': 'Orange, NY',
            'tiger:reviewed': 'no'},
        [221836406, 222284318, 222284314, 222284309, 222284306])]

    def coords(self):
        return [   (221933299, 41.23390700000014, -74.11097500000017),
    (222284381, 41.23390900000003, -74.11074800000007),
    (222284382, 41.23389600000003, -74.11055200000007),
    (355635925, 41.233859400000014, -74.11038630000004),
    (355635926, 41.233840000000015, -74.11021470000004),
    (355635927, 41.233840000000015, -74.11004300000005),
    (355635928, 41.23385290000002, -74.10984560000004),
    (355635929, 41.23393040000002, -74.10914180000005),
    (355635930, 41.233936800000016, -74.10898730000005),
    (355635931, 41.23393040000002, -74.10879850000005),
    (222284291, 41.234589000000035, -74.11534480000009),
    (222215697, 41.23459799999999, -74.11385000000017),
    (222284295, 41.234586000000036, -74.11316600000009),
    (222284299, 41.23455600000003, -74.11278400000009),
    (222284303, 41.23450300000003, -74.11244700000009),
    (222217173, 41.234446999999946, -74.1122020000001),
    (222284306, 41.234392000000035, -74.11202200000008),
    (222284479, 41.23433700000004, -74.11193990000007),
    (222284482, 41.23430700000004, -74.11190500000006),
    (222284486, 41.23422500000004, -74.11181100000006),
    (221836401, 41.234132999999815, -74.11174100000062),
    (222284445, 41.23395700000003, -74.11067600000007),
    (222284448, 41.234001000000035, -74.11074000000006),
    (222284455, 41.234051000000036, -74.11079000000007),
    (221933290, 41.23417700000014, -74.11084900000017),
    (221933296, 41.23398600000014, -74.11088800000017),
    (221933293, 41.23403600000014, -74.11085700000017),
    (221836697, 41.2342209999998, -74.11085500000061),
    (221836695, 41.2342929999998, -74.11089000000061),
    (221836694, 41.2343459999998, -74.1109430000006),
    (221836691, 41.2343999999998, -74.1110220000006),
    (221836416, 41.23445999999981, -74.11114800000061),
    (221836413, 41.23447599999981, -74.11127500000062),
    (221836411, 41.23447199999981, -74.11135900000062),
    (221836409, 41.23445499999981, -74.11145900000062),
    (221836406, 41.234402999999816, -74.11157400000062),
    (221836403, 41.234323999999816, -74.11167300000062),
    (221836402, 41.23424499999982, -74.11172500000062),
    (221836605, 41.234026999999806, -74.1117110000006),
    (221933327, 41.233952000000144, -74.11166900000018),
    (221933324, 41.233850000000146, -74.11154200000017),
    (221933310, 41.233822000000146, -74.11146300000017),
    (221933307, 41.233803000000144, -74.11132100000017),
    (221933304, 41.23381000000014, -74.11119200000017),
    (221933302, 41.23384700000014, -74.11106500000017),
    (222284318, 41.234384000000034, -74.11178100000008),
    (222284314, 41.234386000000036, -74.11187000000008),
    (222284309, 41.234382200000034, -74.11193990000008)]

# This test validates that joining won't spiral back on itself in a roundabout.
def test_collector_joins_cr106_across_roundabout():
    collector = WayCollector(parser_class=CR106Parser)
    collections = []

    collector.parse('doesnt_exist.pbf', callback=lambda collection: collections.append(collection))

    assert collections == []
