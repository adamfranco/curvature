import sys
import math
import resource
from copy import copy
import time
from imposm.parser import OSMParser

# simple class that handles the parsed OSM data.
class WayCollector(object):
    collections = []
    routes = {}
    coords = {}
    num_coords = 0
    num_ways = 0
    verbose = False
    roads = []
    roundabouts = []

    def __init__(self, parser_class=OSMParser):
        self.parser_class = parser_class

    def log(self, msg):
        if self.verbose:
            sys.stderr.write("{}\t{mem:.1f}MB\n".format(msg, mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
            sys.stderr.flush()

    def parse(self, filename, callback):
        # Reinitialize if we have a new file
        self.collections = []
        self.coords = {}
        self.routes = {}
        num_coords = 0
        num_ways = 0
        start_time = time.time()
        self.log("Loading {}".format(filename))
        self.log("Loading ways, each '-' is 100 ways, each row is 10,000 ways")

        p = self.parser_class(ways_callback=self.ways_callback)
        p.parse(filename)

        self.log("\nWays matched in {}".format(filename))
        self.log("{} coordinates will be loaded, each '.' is 1% complete".format(len(self.coords)))

        total = len(self.coords)
        if total < 100:
            self.coords_marker = 1
        else:
            self.coords_marker = round(total/100)

        p = self.parser_class(coords_callback=self.coords_callback)
        p.parse(filename)
        self.log("\nCoordinates loaded")
        self.apply_coordinates()
        self.log("\nApplying coordinates to ways complete")
        self.join_ways()

        # Send our collected data to our callback function.
        self.log("Streaming collections, each '.' is 1% complete")
        if self.verbose:
            total = len(self.collections)
            if total < 100:
                collections_marker = 1
            else:
                collections_marker = round(total/100)
            i = 0
        for collection in self.collections:
            # status output
            if self.verbose:
                i += 1
                if not (i % collections_marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()
            callback(collection)
        self.log('\nStreaming completed in {time:.1f}'.format(time=(time.time() - start_time)))

    def coords_callback(self, coords):
        # callback method for coords
        for osm_id, lon, lat in coords:
            if osm_id in self.coords:
                self.coords[osm_id] = (lat, lon)

                # status output
                if self.verbose:
                    self.num_coords = self.num_coords + 1
                    if not (self.num_coords % self.coords_marker):
                        sys.stderr.write('.')
                        sys.stderr.flush()

    def ways_callback(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags and (not self.roads or tags['highway'] in self.roads):
                # ignore single-point ways
                if len(refs) < 2:
                    self.log('\nSkipping single-point way: id: {}, tags: {}, refs: {}\n'.format(osmid, tags, refs))
                    continue
                way = {'id': osmid, 'tags': tags, 'refs': refs}

                # Add the way to our roundabouts list if it is tagged as a roundabout.
                if 'junction' in tags and tags['junction'] == 'roundabout':
                    self.roundabouts.append(way)

                # Add our ways to a route collection if we can match them either
                # by route-number or alternatively, by name. These route-collections
                # will later be joined into longer segments so that curvature
                # calculations can extend over multiple way-segments that might be
                # split due to bridges, local names, speed limits, or other metadata
                # changes.
                if 'ref' in tags:
                    routes = tags['ref'].split(';')
                    for route in routes:
                        if route not in self.routes:
                            self.routes[route] = {  'join_type': 'ref',
                                                    'join_data': route,
                                                    'ways': []}
                        self.routes[route]['ways'].append(way)
                else:
                    if 'name' in tags and tags['name'] != '':
                        if tags['name'] not in self.routes:
                            self.routes[tags['name']] = {   'join_type': 'name',
                                                            'join_data': tags['name'],
                                                            'ways': []}
                        self.routes[tags['name']]['ways'].append(way)
                    else:
                        self.collections.append({'join_type': 'none', 'ways': [way]})

                for ref in refs:
                    self.coords[ref] = None

                # status output
                if self.verbose:
                    self.num_ways = self.num_ways + 1
                    if not (self.num_ways % 100):
                        sys.stderr.write('-')
                        if not self.num_ways % 10000:
                            sys.stderr.write('\n')
                        sys.stderr.flush()

    # Add the coordinates to each way.
    def apply_coordinates(self):
        # status output
        start_time = time.time()
        i = 0
        total = len(self.routes) + len(self.collections)
        if total < 100:
            marker = 1
        else:
            marker = round(total/100)
        self.log("{} routes & ways have their coordinates added. Each '.' is 1% complete".format(total))

        # Add to joinable-ways.
        for route, route_data in self.routes.iteritems():
            for way in route_data['ways']:
                way['coords'] = map(lambda ref: self.coords[ref], way['refs'])
            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # Add to un-joinable ways.
        for collection in self.collections:
            for way in collection['ways']:
                way['coords'] = map(lambda ref: self.coords[ref], way['refs'])
            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # delete our coords database as we don't need it any more.
        self.coords = []

    def way_sort_key(self, way):
        # To encourage joining that continues along the length of route rather
        # than doubling back on roundabouts, ramps, islands, and other split-route
        # situations, sort the two-direction ways first, followed by one-way ways,
        # followed by roundabout ways.

        key = 'a'
        # put roundabouts last.
        if 'junction' in way['tags']:
            if way['tags']['junction'] == 'roundabout':
                key = 'f'
            elif 'oneway' in way['tags']:
                if way['tags']['oneway'] == 'yes':
                    key = 'e'
                else:
                    # two-way junctions.
                    key = 'c'
        # put one-way after 2-way
        if 'oneway' in way['tags']:
            if way['tags']['oneway'] == 'yes':
                key = 'd'
        # put other link-ways after two-way ways.
        if key == 'a' and '_link' in way['tags']['highway']:
            key = 'b'
        key = '{}-{}'.format(key, str(way['id']).zfill(20))
        return key

    # Join numbered/named routes end-to-end and add them to the way list.
    def join_ways(self):
        # status output
        start_time = time.time()
        i = 0
        total = len(self.routes)
        if total < 100:
            marker = 1
        else:
            marker = round(total/100)
        self.log("{} routes will be joined, each '.' is 1% complete".format(total))

        for route, route_data in self.routes.iteritems():
            # Sort ways so that joining always happens in the same order
            # even if the parser returns them in a different order.
            # ways = sorted(route_data['ways'], key=lambda way: way['id'])
            ways = sorted(route_data['ways'], key=lambda way: self.way_sort_key(way))

            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

            while len(ways) > 0:
                collection = {  'join_type': route_data['join_type'],
                                'join_data': route_data['join_data'],
                                'ways': [ways.pop(0)] }
                # A list of all refs added to a collection. Checking this list will
                # prevent creating non-linar forking structures.
                collection_refs = [collection['ways'][0]['refs']]
                # Loop through all our ways at least as many times as we have ways
                # to be able to catch any that join onto the end after others have
                # been joined on.
                j = 0
                max_loop = len(ways)
                # Start our first iteration with the "collection_modified" flag set to True.
                # After this first loop, if no ways get added to the base_way,
                # there is no reason to keep looping until max_loop
                collection_modified = True
                while collection_modified and j < max_loop:
                    j = j + 1
                    # Set our modification flag to False so we can detect changes
                    # to the base_way.
                    collection_modified = False
                    unused_ways = []
                    # try to join to the begining or end
                    while len(ways) > 0:
                        way = ways.pop(0)
                        modified_this_pass = False
                        # join to the end of the base in order
                        if collection['ways'][-1]['refs'][-1] == way['refs'][0] and way['refs'][-1] not in collection_refs:
                            collection_modified = True
                            modified_this_pass = True
                            collection['ways'].append(way)
                            collection_refs = collection_refs + way['refs']
                        # join to the end of the base in reverse order
                        elif collection['ways'][-1]['refs'][-1] == way['refs'][-1] and way['refs'][0] not in collection_refs:
                            # Make a copy of the way before modifying it as it may be
                            # a member of other routes that will be joined in a different sequence.
                            way_copy = copy(way)
                            way_copy['refs'] = list(reversed(way_copy['refs']))
                            way_copy['coords'] = list(reversed(way_copy['coords']))
                            collection_modified = True
                            modified_this_pass = True
                            collection['ways'].append(way_copy)
                            collection_refs = collection_refs + way_copy['refs']

                        # join to the beginning of the base in order
                        elif collection['ways'][0]['refs'][0] == way['refs'][-1] and way['refs'][0] not in collection_refs:
                            collection_modified = True
                            modified_this_pass = True
                            collection['ways'].insert(0, way)
                            collection_refs =  way['refs'] + collection_refs

                        # join to the beginning of the base in reverse order
                        elif collection['ways'][0]['refs'][0] == way['refs'][0] and way['refs'][-1] not in collection_refs:
                            # Make a copy of the way before modifying it as it may be
                            # a member of other routes that will be joined in a different sequence.
                            way_copy = copy(way)
                            collection_modified = True
                            modified_this_pass = True
                            way_copy['refs'] = list(reversed(way_copy['refs']))
                            way_copy['coords'] = list(reversed(way_copy['coords']))
                            collection['ways'].insert(0, way_copy)
                            collection_refs = way_copy['refs'] + collection_refs
                        else:
                            unused_ways.append(way)
                        # If we've modified our collection with a new end-way, start looping
                        # again from our sorted list so that we join in the correct order.
                        if modified_this_pass:
                            ways = unused_ways + ways
                            unused_ways = []

                    # Continue on joining the rest of the ways in this route.
                    ways = unused_ways

                    # Try to find a roundabout segment that will bridge between
                    # one of our collection ends and one of the other remaining ways.
                    # Roundabouts may or may not be tagged with our road name or
                    # route number.
                    if len(ways):
                        roundabout_segment = self.get_roundabout_segment(collection, ways)
                        if roundabout_segment:
                            ways.insert(0, roundabout_segment)

                # After we've either added all of the ways or looped the max_loop times,
                # add this collection to our collections list and return to the start
                # of our `while len(ways) > 0:` loop. The next remaining way in the
                # ways list will become the basis for a new collection that may get
                # some more of the remaining ways joined to it.
                self.collections.append(collection)
        self.log('\nJoining completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))

    def get_roundabout_segment(self, collection, remaining_ways):
        # Find roundabouts that connect to our start or end points.
        collection_start = collection['ways'][0]['refs'][0]
        collection_end = collection['ways'][-1]['refs'][-1]
        candidates = []
        for way in self.roundabouts:
            for i, ref in enumerate(way['refs']):
                if ref == collection_start or ref == collection_end:
                    candidates.append(self.extract_roundabout_segment(way, i))
                    break

        # Find the first remaining way that has a start/end point shared with one of
        # our roundabout candidates.
        for segment in candidates:
            # Go through each point in our roundabout and check to see if we can
            # attach a remaining way to it. Doing so in this order will catch the first
            # entrance/exit we come to.
            for end_i, end_ref in enumerate(segment['refs']):
                for remaining_way in remaining_ways:
                    remaining_way_start = way['refs'][0]
                    remaining_way_end = way['refs'][-1]
                    if end_ref == remaining_way_start or end_ref == remaining_way_end:
                        # We've found a link. Remove the remaining points from the segment.
                        if end_i == len(segment['refs']) - 1:
                            return segment
                        else:
                            slice_end = end_i + 1
                            segment['refs'] = segment['refs'][0][0:slice_end]
                            if 'coords' in segment:
                                segment['coords'] = segment['coords'][0:slice_end]
                        return segment

    def extract_roundabout_segment(self, way, start_index):
        segment = copy(way)
        # for non-circular roundabout ways, drop the points before our start_index
        if segment['refs'][0] != segment['refs'][-1]:
            segment['refs'] = segment['refs'][start_index:]
            if 'coords' in segment:
                segment['coords'] = segment['coords'][start_index:]
        # For circular roundabout ways, make the start_index the first element,
        # but include all remaining refs.
        else:
            # Add our refs from the start to the last element of the array.
            segment['refs'] = segment['refs'][start_index:]
            if 'coords' in segment:
                segment['coords'] = segment['coords'][start_index:]
            # Add our refs from 1 to the start_index, dropping the duplicate start/end point
            # and the duplicate start-index point (segment will no longer be fully circular).
            segment['refs'] = segment['refs'][1:start_index]
            if 'coords' in segment:
                segment['coords'] = segment['coords'][1:start_index]
        return segment
