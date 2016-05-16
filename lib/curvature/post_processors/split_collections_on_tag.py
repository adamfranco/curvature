# -*- coding: UTF-8 -*-
import argparse
from curvature.collection_tools import CollectionSplitter

class SplitCollectionsOnTag(CollectionSplitter):
    def __init__(self, tag=None, group=None, exclude_ways_missing_tag=False):
        self.tag = tag
        self.group = group
        self.exclude_ways_missing_tag = exclude_ways_missing_tag

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(description='Split collections when a tag is encountered  that is not in the input group. Collections will be split into sub-collections that are either all in the group or all out of the group.')
        parser.add_argument('--exclude_ways_missing_tag', action='store_true', help='Also split when a way doesn\'t have the tag set. Default is to considder ways missing the tag to be in the group.')
        parser.add_argument('--tag', type=str, help='The tag to split on. Example: highway')
        parser.add_argument('--group', type=str, help='The tag values in the primary group. Example: motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link')
        args = parser.parse_args(argv)
        return cls(args.tag, args.group.split(','), args.exclude_ways_missing_tag)

    def process(self, iterable):
        for collection in iterable:
            result_collection = self.create_result_collection(collection)
            previous_in_group = self.way_in_group(collection['ways'][0])
            for way in collection['ways']:
                way_in_group = self.way_in_group(way)
                if way_in_group == previous_in_group:
                    result_collection['ways'].append(way)
                else:
                    # yield the previous portion of the collection and start
                    # a new portion with the alternate in-group state.
                    yield(result_collection)
                    result_collection = self.create_result_collection(collection)
                    result_collection['ways'].append(way)
                    previous_in_group = way_in_group
            # Yield the remaining collection.
            yield(result_collection)

    def way_in_group(self, way):
        if not self.exclude_ways_missing_tag and not self.tag in way['tags']:
            return True
        if self.tag in way['tags'] and way['tags'][self.tag] in self.group:
            return True
        else:
            return False
