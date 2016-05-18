# -*- coding: UTF-8 -*-
import argparse

class FilterCollectionsByNumWays(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='filter_collections_by_num_ways', description='Filter collections matching the number of ways specified.')
        parser.add_argument('--min', type=int, default=0, help='The minimum number of constituent ways a collection may have. Default is 0, no-min.')
        parser.add_argument('--max', type=int, default=0, help='The minimum number of constituent ways a collection may have. Default is 0, no-max.')
        args = parser.parse_args(argv)
        return cls(args.min, args.max)

    def process(self, iterable):
        for collection in iterable:
            if self.min > 0:
                if len(collection['ways']) < self.min:
                    continue
            if self.max > 0:
                if len(collection['ways']) > self.max:
                    continue
            yield(collection)
