# -*- coding: UTF-8 -*-
import argparse

class AddSegmentCurvature(object):

    level_1_max_radius = 175
    level_1_weight = 1
    level_2_max_radius = 100
    level_2_weight = 1.3
    level_3_max_radius = 60
    level_3_weight = 1.6
    level_4_max_radius = 30
    level_4_weight = 2

    def __init__(self, l1maxr=175, l2maxr=100, l3maxr=60, l4maxr=30, l1weight=1, l2weight=1.3, l3weight=1.6, l4weight=2):
        self.level_1_max_radius = l1maxr
        self.level_1_weight = l1weight
        self.level_2_max_radius = l2maxr
        self.level_2_weight = l2weight
        self.level_3_max_radius = l3maxr
        self.level_3_weight = l3weight
        self.level_4_max_radius = l4maxr
        self.level_4_weight = l4weight

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='add_segment_curvature', description='Add weighted curvature values to each segment based on radius and length.')
        parser.add_argument('--l1maxr', type=int, default=175, help='The maximum radius to be considered a broad curve.')
        parser.add_argument('--l2maxr', type=int, default=100, help='The maximum radius to be considered a medium-broad curve.')
        parser.add_argument('--l3maxr', type=int, default=60, help='The maximum radius to be considered a medium-sharp curve.')
        parser.add_argument('--l4maxr', type=int, default=30, help='The maximum radius to be considered a sharp curve.')
        parser.add_argument('--l1weight', type=float, default=1, help='The weight to multiply broad curve lengths by.')
        parser.add_argument('--l2weight', type=float, default=1.3, help='The weight to multiply medium-broad curve lengths by.')
        parser.add_argument('--l3weight', type=float, default=1.6, help='The weight to multiply medium-sharp curve lengths by.')
        parser.add_argument('--l4weight', type=float, default=2, help='The weight to multiply sharp curve lengths by.')
        args = parser.parse_args(argv)
        return cls(args.l1maxr, args.l2maxr, args.l3maxr, args.l4maxr, args.l1weight, args.l2weight, args.l3weight, args.l4weight)

    def process(self, iterable):
        for collection in iterable:
            all_segments = []
            for way in collection['ways']:
                if 'segments' not in way:
                    raise ValueError('Required "segments" not found in way. Add them with `curvature-pp add_segments` before using this processor.')
                for segment in way['segments']:
                    self.add_curvature_to_segment(segment)
            yield(collection)

    def add_curvature_to_segment(self, segment):
        if 'length' not in segment or 'radius' not in segment:
            raise ValueError('Required "length" or "radius" not found in segment. Add them with `curvature-pp add_segment_length_and_radii` before using this processor.')
        if segment['radius'] < self.level_4_max_radius:
            segment['curvature_level'] = 4
            segment['curvature'] = segment['length'] * self.level_4_weight
        elif segment['radius'] < self.level_3_max_radius:
            segment['curvature_level'] = 3
            segment['curvature'] =  segment['length'] * self.level_3_weight
        elif segment['radius'] < self.level_2_max_radius:
            segment['curvature_level'] = 2
            segment['curvature'] =  segment['length'] * self.level_2_weight
        elif segment['radius'] < self.level_1_max_radius:
            segment['curvature_level'] = 1
            segment['curvature'] =  segment['length'] * self.level_1_weight
        else:
            segment['curvature_level'] = 0
            segment['curvature'] =  0
