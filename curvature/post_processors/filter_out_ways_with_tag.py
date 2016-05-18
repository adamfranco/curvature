# -*- coding: UTF-8 -*-
import argparse
from curvature.collection_tools import CollectionSplitter

class FilterOutWaysWithTag(CollectionSplitter):
    def __init__(self, tag=None, values=None, filter_out_ways_missing_tag=False):
        self.tag = tag
        self.values = values
        self.filter_out_ways_missing_tag = filter_out_ways_missing_tag

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='filter_out_ways_with_tag', description='Filter out ways that have one of the tags listed.')
        parser.add_argument('--filter_out_ways_missing_tag', action='store_true', help='Also filter out ways that don\'t have the tag set. Default is to keep ways without the tag set.')
        parser.add_argument('--tag', type=str, help='The tag to filter on. Example: highway')
        parser.add_argument('--values', type=str, help='The tag values filter when found. Example: track,path,cycleway,footway')
        args = parser.parse_args(argv)
        return cls(args.tag, args.values.split(','), args.filter_out_ways_missing_tag)

    def process(self, iterable):
        for collection in iterable:
            result_collection = self.create_result_collection(collection)
            for way in collection['ways']:
                # If we've hit a matching way, yield any previous results and start a new collection.
                # No need to yield anything if we don't have any previous results.
                if self.way_matches(way):
                    if result_collection['ways']:
                        yield(result_collection)
                        result_collection = self.create_result_collection(collection)
                else:
                    result_collection['ways'].append(way)

            # Yield the remaining collection.
            if result_collection['ways']:
                yield(result_collection)

    def way_matches(self, way):
        if self.filter_out_ways_missing_tag and not self.tag in way['tags']:
            return True
        if self.tag in way['tags'] and way['tags'][self.tag] in self.values:
            return True
        else:
            return False
