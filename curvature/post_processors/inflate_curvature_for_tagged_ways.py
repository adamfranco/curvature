# -*- coding: UTF-8 -*-
import argparse

class InflateCurvatureForTaggedWays(object):
    def __init__(self, curvature=1, tag=None, values=None):
        self.curvature = curvature
        self.tag = tag
        self.values = values

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='inflate_curvature_for_tagged_ways', description='Inflate the curvature on ways with certain properties.')
        parser.add_argument('--curvature', type=int, default=1, help='The ammount of curvature to inflate')
        parser.add_argument('--tag', type=str, required=True, help='The tag to match on. Example: junction')
        parser.add_argument('--values', type=str, help='The tag values which will trigger squashing when found. Example: roundabout,circular')
        args = parser.parse_args(argv)
        if args.values:
            values = args.values.split(',')
        else:
            values = None
        return cls(args.curvature, args.tag, values)

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                # If we've hit a matching way, add to its curvature.
                if self.way_matches(way):
                    total_added = 0
                    for segment in way['segments']:
                        total_added = total_added + self.curvature
                        if 'curvature' in segment:
                            segment['curvature'] = segment['curvature'] + self.curvature
                        else:
                            segment['curvature'] = self.curvature
                        if 'curvature_level' in segment and segment['curvature_level'] < 4:
                            segment['curvature_level'] = segment['curvature_level'] + 1
                    total_added = max(total_added, self.curvature)
                    if 'curvature' in way:
                        way['curvature'] = way['curvature'] + total_added
                    else:
                        way['curvature'] = total_added
            yield(collection)

    def way_matches(self, way):
        if self.tag in way['tags']:
            if self.values is None:
                return True
            elif way['tags'][self.tag] in self.values:
                return True
        return False
