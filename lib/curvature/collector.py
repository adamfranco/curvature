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

    def __init__(self, parser_class=OSMParser):
        self.parser_class = parser_class

    def parse(self, filename, callback):
        # Reinitialize if we have a new file
        collections = []
        coords = {}
        num_coords = 0
        num_ways = 0
        if self.verbose:
            sys.stderr.write("\nLoading {}".format(file.name))

        # status output
        if self.verbose:
            sys.stderr.write("\nLoading ways, each '-' is 100 ways, each row is 10,000 ways\n")

        p = self.parser_class(ways_callback=self.ways_callback)
        p.parse(filename)

        # status output
        if self.verbose:
            sys.stderr.write("\nWays matched in {} {mem:.1f}MB memory used,\n{} coordinates will be loaded, each '.' is 1% complete\n".format(filename, len(self.coords), mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))

            total = len(self.coords)
            if total < 100:
                self.coords_marker = 1
            else:
                self.coords_marker = round(total/100)

        p = self.parser_class(coords_callback=self.coords_callback)
        p.parse(filename)

        # status output
        if self.verbose:
            sys.stderr.write("\nCoordinates loaded {mem:.1f}MB memory used.".format(mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
            sys.stderr.flush()

        self.apply_coordinates()

        # status output
        if self.verbose:
            sys.stderr.write("\nApplying coordinates to ways complete. {mem:.1f}MB memory used.".format(mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))

        # Join routes end-to-end and add them to the way list.
        self.join_ways()

        # status output
        if self.verbose:
            sys.stderr.write("\nJoining complete. {mem:.1f}MB memory used.".format(mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
            sys.stderr.flush()

        if self.verbose:
            total = len(self.collections)
            sys.stderr.write("\nStreaming data for {} collections. Each '.' is 1% complete\n".format(total))
            if total < 100:
                marker = 1
            else:
                marker = round(total/100)
            i = 0
            start_time = time.time()

        for collection in self.collections:
            callback(collection)
            if self.verbose:
                i += 1
                if not i % marker:
                    sys.stderr.write('.')

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

            # ignore circular ways (Maybe we don't need this)
            if refs[0] == refs[-1]:
                continue
            if 'highway' in tags and (not self.roads or tags['highway'] in self.roads):
                way = {'id': osmid, 'tags': tags, 'refs': refs}

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
                            self.routes[route] = []
                        self.routes[route].append(way)
                else:
                    if 'name' in tags and tags['name'] != '':
                        if tags['name'] not in self.routes:
                            self.routes[tags['name']] = []
                        self.routes[tags['name']].append(way)
                    else:
                        self.collections.append([way])

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
        if self.verbose:
            start_time = time.time()
            i = 0
            total = len(self.routes) + len(self.collections)
            if total < 100:
                marker = 1
            else:
                marker = round(total/100)
            sys.stderr.write("\n{} routes & ways have their coordinates added. Each '.' is 1% complete\n".format(total))
            sys.stderr.flush()

        # Add to joinable-ways.
        for route, ways in self.routes.iteritems():
            for way in ways:
                way['coords'] = []
                for ref in way['refs']:
                    way['coords'].append(self.coords[ref])
            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # Add to un-joinable ways.
        for collection in self.collections:
            for way in collection:
                way['coords'] = []
                for ref in way['refs']:
                    way['coords'].append(self.coords[ref])
            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # delete our coords database as we don't need it any more.
        self.coords = []

    # Join numbered/named routes end-to-end and add them to the way list.
    def join_ways(self):
        # status output
        if self.verbose:
            start_time = time.time()
            i = 0
            total = len(self.routes)
            if total < 100:
                marker = 1
            else:
                marker = round(total/100)
            sys.stderr.write("\n{} routes will be joined, each '.' is 1% complete\n".format(total))
            sys.stderr.flush()

        for route, ways in self.routes.iteritems():
            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

            while len(ways) > 0:
                collection = [ways.pop()]
                # A list of all refs added to a collection. Checking this list will
                # prevent creating non-linar forking structures.
                collection_refs = [collection[0]['refs']]
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
                        way = ways.pop()
                        # join to the end of the base in order
                        if collection[-1]['refs'][-1] == way['refs'][0] and way['refs'][-1] not in collection_refs:
                            collection_modified = True
                            collection.append(way)
                            collection_refs = collection_refs + way['refs']
                        # join to the end of the base in reverse order
                        elif collection[-1]['refs'][-1] == way['refs'][-1] and way['refs'][0] not in collection_refs:
                            # Make a copy of the way before modifying it as it may be
                            # a member of other routes that will be joined in a different sequence.
                            way_copy = copy(way)
                            way_copy['refs'] = list(reversed(way_copy['refs']))
                            way_copy['coords'] = list(reversed(way_copy['coords']))
                            collection_modified = True
                            collection.append(way_copy)
                            collection_refs = collection_refs + way_copy['refs']

                        # join to the beginning of the base in order
                        elif collection[0]['refs'][0] == way['refs'][-1] and way['refs'][0] not in collection_refs:
                            collection_modified = True
                            collection.insert(0, way)
                            collection_refs =  way['refs'] + collection_refs

                        # join to the beginning of the base in reverse order
                        elif collection[0]['refs'][0] == way['refs'][0] and way['refs'][-1] not in collection_refs:
                            # Make a copy of the way before modifying it as it may be
                            # a member of other routes that will be joined in a different sequence.
                            way_copy = copy(way)
                            collection_modified = True
                            way_copy['refs'] = list(reversed(way_copy['refs']))
                            way_copy['coords'] = list(reversed(way_copy['coords']))
                            collection.insert(0, way_copy)
                            collection_refs = way_copy['refs'] + collection_refs
                        else:
                            unused_ways.append(way)
                    # Continue on joining the rest of the ways in this route.
                    ways = unused_ways
                # Add this base way to our ways list
                self.collections.append(collection)
        if self.verbose:
            sys.stderr.write('\nJoining completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))
