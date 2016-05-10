# -*- coding: UTF-8 -*-
import argparse

class FilterOnlyWaysWithTag(object):
    def __init__(self, tag=None, values=None, skip_ways_missing_tag=False):
        self.tag = tag
        self.values = values
        self.skip_ways_missing_tag = skip_ways_missing_tag

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(description='Filter out ways that have one of the tags listed.')
        parser.add_argument('--tag', type=str, help='The tag to filter on. Example: highway')
        parser.add_argument('--values', type=str, help='The tag values to match Example: motorway,trunk,primary,secondary,tertiary,unclassified,residential')
        parser.add_argument('--skip_ways_missing_tag', action='store_true', help='Don\'t include ways that don\'t have the tag set. Default is to keep ways without the tag set.')
        args = parser.parse_args(argv)
        return cls(args.tag, args.values.split(','), args.skip_ways_missing_tag)

    def process(self, iterable):
        for collection in iterable:
            result_collection = []
            for way in collection:
                # If we've hit a matching way, yield any previous results and start a new collection.
                # No need to yield anything if we don't have any previous results.
                if self.way_matches(way):
                    result_collection.append(way)
                else:
                    if result_collection:
                        yield(result_collection)
                        result_collection = []

            # Yield the remaining collection.
            if result_collection:
                yield(result_collection)

    def way_matches(self, way):
        if not self.skip_ways_missing_tag and not self.tag in way['tags']:
            return True
        if self.tag in way['tags'] and way['tags'][self.tag] in self.values:
            return True
        else:
            return False
