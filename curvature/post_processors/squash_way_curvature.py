# -*- coding: UTF-8 -*-
import argparse

class SquashWayCurvature(object):
    def __init__(self, tag=None, values=None):
        self.tag = tag
        self.values = values

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='squash_way_curvature', description='Squash the curvature on ways with certain properties.')
        parser.add_argument('--tag', type=str, required=True, help='The tag to match on. Example: junction')
        parser.add_argument('--values', type=str, required=True, help='The tag values which will trigger squashing when found. Example: roundabout,circular')
        args = parser.parse_args(argv)
        return cls(args.tag, args.values.split(','))

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                # If we've hit a matching way, set its curvature to 0.
                if self.way_matches(way):
                    if 'curvature' in way.keys():
                        way['curvature'] = 0
                    for segment in way['segments']:
                        if 'curvature' in segment.keys():
                            segment['curvature'] = 0
                        if 'curvature_level' in segment.keys():
                            segment['curvature_level'] = 0
            yield(collection)

    def way_matches(self, way):
        if self.tag in way['tags'].keys() and way['tags'][self.tag] in self.values:
            return True
        else:
            return False
