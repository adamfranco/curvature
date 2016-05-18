# -*- coding: UTF-8 -*-
import argparse
from curvature.collection_tools import CollectionSplitter

class FilterOnlyWaysWithTag(CollectionSplitter):
    def __init__(self, tag=None, values=None, include_ways_missing_tag=False):
        self.tag = tag
        self.values = values
        self.include_ways_missing_tag = include_ways_missing_tag

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='filter_only_ways_with_tag', description='Filter out ways that have one of the tags listed.')
        parser.add_argument('--tag', type=str, required=True, help='The tag to filter on. Example: highway')
        parser.add_argument('--values', type=str, required=True, help='The tag values to match Example: motorway,trunk,primary,secondary,tertiary,unclassified,residential')
        parser.add_argument('--include_ways_missing_tag', action='store_true', help='Include ways that don\'t have the tag set. Default is to exclude without the tag set.')
        args = parser.parse_args(argv)
        return cls(args.tag, args.values.split(','), args.include_ways_missing_tag)

    def process(self, iterable):
        for collection in iterable:
            result_collection = self.create_result_collection(collection)
            for way in collection['ways']:
                # If we've hit a matching way, yield any previous results and start a new collection.
                # No need to yield anything if we don't have any previous results.
                if self.way_matches(way):
                    result_collection['ways'].append(way)
                else:
                    if result_collection['ways']:
                        yield(result_collection)
                        result_collection = self.create_result_collection(collection)

            # Yield the remaining collection.
            if result_collection['ways']:
                yield(result_collection)

    def way_matches(self, way):
        if self.include_ways_missing_tag and not self.tag in way['tags']:
            return True
        if self.tag in way['tags'] and way['tags'][self.tag] in self.values:
            return True
        else:
            return False
