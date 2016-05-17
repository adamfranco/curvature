# -*- coding: UTF-8 -*-
import argparse

class FilterCollectionsByLength(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(description='Filter out collections not meeting our length levels.')
        parser.add_argument('--min', type=float, default=None, help='The minimum length level to be included in the output, e.g. 300, default 0 means no minum')
        parser.add_argument('--max', type=float, default=None, help='The maximum length level to be included in the output, e.g. 5000, default 0 means no maximum')
        args = parser.parse_args(argv)
        return cls(args.min, args.max)

    def process(self, iterable):
        for collection in iterable:
            # Use an already-summed length value if it exists on the collection.
            if 'length' in collection:
                length = collection['length']
            else:
                length = 0
                for way in collection['ways']:
                    # Use an already-summed length value if it exists on the way.
                    if 'length' in way:
                        length += way['length']
                    # If not, sum the length of the segments
                    else:
                        for segment in way['segments']:
                            length += segment['length']

            if self.min is not None:
                if length < self.min:
                    continue
            if self.max is not None:
                if length > self.max:
                    continue
            yield(collection)
