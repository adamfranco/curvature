# -*- coding: UTF-8 -*-
import argparse
from curvature.collection_tools import InflateCurvatureNearbyProcessorAbstract

class InflateCurvatureNearWayTagChange(InflateCurvatureNearbyProcessorAbstract):
    def __init__(self, curvature=1, tag=None, only_values=None, ignored_values=None, distance=0):
        self.tag = tag
        self.only_values = only_values
        self.ignored_values = ignored_values
        super().__init__(curvature, distance)

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='inflate_curvature_near_way_tag_change', description='Inflate the curvature on segments close to where the tags change on ways.')
        parser.add_argument('--curvature', type=int, default=1, help='The ammount of curvature to inflate')
        parser.add_argument('--tag', type=str, required=True, help='The tag to match on. Example: oneway')
        parser.add_argument('--only-values', type=str, help='Only look at these values, treat all others as empty. Example: roundabout,circular')
        parser.add_argument('--ignored-values', type=str, help='Values that will be treated the same as if they were not set. Example: no')
        parser.add_argument('--distance', type=int, required=True, help='The number of meters forward and backward at which to inflate curvature. Example: 30')
        args = parser.parse_args(argv)
        if args.only_values:
            only_values = args.only_values.split(',')
        else:
            only_values = None
        if args.ignored_values:
            ignored_values = args.ignored_values.split(',')
        else:
            ignored_values = None
        return cls(args.curvature, args.tag, only_values, ignored_values, args.distance)

    def process_collection(self, collection):
        current_value = self.get_value_from_way(collection['ways'][0])
        for i, way in enumerate(collection['ways']):
            new_value = self.get_value_from_way(way)
            if new_value != current_value:
                self.inflate_segment_curvature_nearby(collection, i, 0, 'start')
                current_value = new_value
        return collection

    def get_value_from_way(self, way):
        if self.tag in way['tags']:
            if self.only_values is not None:
                if way['tags'][self.tag] in self.only_values:
                    return way['tags'][self.tag]
                else:
                     return None
            else:
                if way['tags'][self.tag] in self.ignored_values:
                    return None
                else:
                    return way['tags'][self.tag]
        return None
