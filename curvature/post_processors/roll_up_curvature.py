# -*- coding: UTF-8 -*-
import argparse

class RollUpCurvature(object):
    def __init__(self, add_to_ways=True, add_to_collections=True):
        self.add_to_ways = add_to_ways
        self.add_to_collections = add_to_collections

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='roll_up_curvature', description='Roll up the sum of the curvature of segements to each way and/or collection (default both).')
        parser.add_argument('--skip_ways', action='store_true', help='Don\'t sum the curvature into the ways, only the collections.')
        parser.add_argument('--skip_collections', action='store_true', help='Don\'t sum the curvature into the collections, only the ways.')
        args = parser.parse_args(argv)
        if args.skip_ways and args.skip_collections:
            raise RuntimeError('Cannot skip both ways and collections, there would be nothing to do.')
        return cls(not args.skip_ways, not args.skip_collections)

    def process(self, iterable):
        for collection in iterable:
            collection_sum = 0
            for way in collection['ways']:
                way_sum = 0
                for segment in way['segments']:
                    way_sum += segment['curvature']
                    collection_sum += segment['curvature']
                if self.add_to_ways:
                    way['curvature'] = way_sum
            if self.add_to_collections:
                collection['curvature'] = collection_sum
            yield(collection)
