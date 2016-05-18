# -*- coding: UTF-8 -*-
import argparse
class SortCollectionsBySum(object):
    def __init__(self, key, reverse=False):
        self.reverse = reverse
        self.key = key

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='sort_collections_by_sum', description='Sort collections in the stream by the sum of one of their values. (e.g. curvature, length)')
        parser.add_argument('--key', type=str, required=True, default='curvature', help='The key to sort on, default: curvature')
        parser.add_argument('--direction', choices=['DESC', 'ASC'], default='DESC', help='The sort direction, ASC or DESC. Default: DESC')
        args = parser.parse_args(argv)
        if args.direction == 'ASC':
            reverse = False
        else:
            reverse = True

        return cls(args.key, reverse)

    def process(self, iterable):
        collections = sorted(iterable, key=lambda c: self.sum_for_collection(c), reverse=self.reverse)
        for collection in collections:
            yield(collection)

    def sum_for_collection(self, collection):
        # Use an already-summed value if it exists on the way.
        if self.key in collection:
            return collection[self.key]

        # Add up the values from the ways
        total = 0
        for way in collection['ways']:
            # Use an already-summed value if it exists on the way.
            if self.key in way:
                total += way[self.key]
            # If not, sum the values of the segments
            else:
                for segment in way['segments']:
                    total += segment[self.key]
        return total
