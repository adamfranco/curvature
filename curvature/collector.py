import sys
import math
import resource
from copy import copy
import time
import osmium
from osmium._osmium import InvalidLocationError

# simple class that handles the parsed OSM data.
class WayCollector(osmium.SimpleHandler):
    collections = []
    routes = {}
    coords = {}
    tagged_nodes = {}
    num_coords = 0
    num_ways = 0
    num_nodes = 0
    verbose = False
    roads = []

    def __init__(self):
        osmium.SimpleHandler.__init__(self)

    def log(self, msg):
        if self.verbose:
            sys.stderr.write("{}\t{mem:.1f}MB\n".format(msg, mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
            sys.stderr.flush()

    def parse(self, filename, callback):
        # Reinitialize if we have a new file
        self.collections = []
        self.coords = {}
        self.routes = {}
        self.tagged_nodes = {}
        num_coords = 0
        num_ways = 0
        num_nodes = 0
        start_time = time.time()
        self.log("Loading {}".format(filename))
        self.log("Loading ways and nodes, each '-' is 100 ways, each '.' is 100 nodes, each row is 10,000 ways or nodes")

        self.apply_file(filename, locations=True, idx='sparse_mem_array')

        self.log("\nWays and nodes loaded matched in {}".format(filename))

        self.join_ways()
        self.attach_tagged_nodes_to_ways()

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

    # Save tagged nodes save the full details for later adding to ways.
    def node(self, node):
        if node.tags:
            new_node = {
                'tags': {},
                'lat': node.location.lat,
                'lon': node.location.lon,
            }
            for tag in node.tags:
                new_node['tags'][tag.k] = tag.v
            self.tagged_nodes[node.id] = new_node

            # status output
            if self.verbose:
                self.num_nodes = self.num_nodes + 1
                if not (self.num_nodes % 100):
                    sys.stderr.write('.')
                    if not (self.num_nodes % 10000):
                        sys.stderr.write('\n')
                    sys.stderr.flush()

    def way(self, way):
        # callback method for ways
        if 'highway' in way.tags and (not self.roads or way.tags['highway'] in self.roads):
            # ignore single-point ways
            if len(way.nodes) < 2:
                self.log('\nSkipping single-point way: id: {}, tags: {}, nodes: {}\n'.format(way.id, way.tags, way.nodes))
                return

            new_way = {'id': way.id, 'tags': {}, 'refs': [], 'coords': [], 'nodes': {}}
            for tag in way.tags:
                new_way['tags'][tag.k] = tag.v
            for node in way.nodes:
                try:
                    new_way['refs'].append(node.ref)
                    new_way['coords'].append((node.lat, node.lon))
                except InvalidLocationError as e:
                    self.log('\nSkipping node: {} (x={}, y={}) because of error: {}\n'.format(node.ref, node.x, node.y, e))

            # Add our ways to a route collection if we can match them either
            # by route-number or alternatively, by name. These route-collections
            # will later be joined into longer segments so that curvature
            # calculations can extend over multiple way-segments that might be
            # split due to bridges, local names, speed limits, or other metadata
            # changes.
            if 'ref' in new_way['tags']:
                routes = new_way['tags']['ref'].split(';')
                for route in routes:
                    if route not in self.routes:
                        self.routes[route] = {  'join_type': 'ref',
                                                'join_data': route,
                                                'ways': []}
                    self.routes[route]['ways'].append(new_way)
            else:
                if 'name' in new_way['tags'] and new_way['tags']['name'] != '':
                    if new_way['tags']['name'] not in self.routes:
                        self.routes[new_way['tags']['name']] = {   'join_type': 'name',
                                                        'join_data': new_way['tags']['name'],
                                                        'ways': []}
                    self.routes[new_way['tags']['name']]['ways'].append(new_way)
                else:
                    self.collections.append({'join_type': 'none', 'ways': [new_way]})

            # status output
            if self.verbose:
                if not self.num_ways:
                    sys.stderr.write('\n')
                self.num_ways = self.num_ways + 1
                if not (self.num_ways % 100):
                    sys.stderr.write('-')
                    if not (self.num_ways % 10000):
                        sys.stderr.write('\n')
                    sys.stderr.flush()

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

        for route, route_data in self.routes.items():
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
                # After we've either added all of the ways or looped the max_loop times,
                # add this collection to our collections list and return to the start
                # of our `while len(ways) > 0:` loop. The next remaining way in the
                # ways list will become the basis for a new collection that may get
                # some more of the remaining ways joined to it.
                self.collections.append(collection)
        self.log('\nJoining completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))

    # Attach tagged nodes to ways that reference them.
    def attach_tagged_nodes_to_ways(self):
        # status output
        start_time = time.time()
        i = 0
        total = len(self.collections)
        if total < 100:
            marker = 1
        else:
            marker = round(total/100)
        self.log("{} collections will have tagged nodes added '.' is 1% complete".format(total))

        for collection in self.collections:
            for way in collection['ways']:
                for j, ref in enumerate(way['refs']):
                    if ref in self.tagged_nodes:
                        # Add the node to the way.
                        way['nodes'][ref] = self.tagged_nodes[ref]
                        # Add the ref to the coords tuple to associate it.
                        way['coords'][j] = (way['coords'][j][0], way['coords'][j][1], ref)

            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # Remove remaining tagged nodes as they are no longer needed.
        del self.tagged_nodes

        # status output
        if self.verbose:
            self.log('\nAdding tagged nodes completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))
