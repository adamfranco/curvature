# -*- coding: UTF-8 -*-
import argparse

class FilterCollectionsByCurvature(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='filter_collections_by_curvature', description='Filter out collections not meeting our curvature levels.')
        parser.add_argument('--min', type=float, default=None, help='The minimum curvature level to be included in the output, e.g. 300')
        parser.add_argument('--max', type=float, default=None, help='The maximum curvature level to be included in the output, e.g. 5000')
        args = parser.parse_args(argv)
        return cls(args.min, args.max)

    def process(self, iterable):
        for collection in iterable:
            # Use an already-summed curvature value if it exists on the collection.
            if 'curvature' in collection:
                curvature = collection['curvature']
            else:
                curvature = 0
                for way in collection['ways']:
                    # Use an already-summed curvature value if it exists on the way.
                    if 'curvature' in way:
                        curvature += way['curvature']
                    # If not, sum the curvature of the segments
                    else:
                        for segment in way['segments']:
                            curvature += segment['curvature']

            if self.min is not None:
                if curvature < self.min:
                    continue
            if self.max is not None:
                if curvature > self.max:
                    continue
            yield(collection)
