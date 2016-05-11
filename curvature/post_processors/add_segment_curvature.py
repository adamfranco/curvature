# -*- coding: UTF-8 -*-

class AddSegmentCurvature(object):

    level_1_max_radius = 175
    level_1_weight = 1
    level_2_max_radius = 100
    level_2_weight = 1.3
    level_3_max_radius = 60
    level_3_weight = 1.6
    level_4_max_radius = 30
    level_4_weight = 2

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            all_segments = []
            for way in collection:
                if 'segments' not in way:
                    raise ValueError('Required "segments" not found in way. Add them with `curvature-pp add_segments` before using this processor.')
                for segment in way['segments']:
                    segment['curvature'] = self.curvature_for_segment(segment)
            yield(collection)

    def curvature_for_segment(self, segment):
        if 'length' not in segment or 'radius' not in segment:
            raise ValueError('Required "length" or "radius" not found in segment. Add them with `curvature-pp add_segment_length_and_radii` before using this processor.')
        if segment['radius'] < self.level_4_max_radius:
            return segment['length'] * self.level_4_weight
        elif segment['radius'] < self.level_3_max_radius:
            return segment['length'] * self.level_3_weight
        elif segment['radius'] < self.level_2_max_radius:
            return segment['length'] * self.level_2_weight
        elif segment['radius'] < self.level_1_max_radius:
            return segment['length'] * self.level_1_weight
        else:
            return 0
