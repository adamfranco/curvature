# -*- coding: UTF-8 -*-
import argparse
class SortCollectionsBySum(object):
    def __init__(self, key, reverse=False):
        self.reverse = reverse
        self.key = key

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(description='Sort collections in the stream by the sum of one of their values. (e.g. curvature, length)')
        parser.add_argument('--key', type=str, default='curvature', help='The key to sort on, default: curvature')
        parser.add_argument('--direction', type=str, default='DESC', help='The sort direction, ASC or DESC. Default: DESC')
        args = parser.parse_args(argv)
        if args.direction == 'ASC':
            reverse = False
        elif args.direction == 'DESC':
            reverse = True
        else:
            raise RuntimeError("\n--direction must be ASC or DESC.")

        return cls(args.key, reverse)

    def process(self, iterable):
        collections = sorted(iterable, key=lambda c: self.sum_for_collection(c), reverse=self.reverse)
        for collection in collections:
            yield(collection)

    def sum_for_collection(self, collection):
        total = 0
        for way in collection:
            # Use an already-summed value if it exists on the way.
            if self.key in way:
                total += way[self.key]
            # If not, sum the values of the segments
            else:
                for segment in way['segments']:
                    total += segment[self.key]
        return total
