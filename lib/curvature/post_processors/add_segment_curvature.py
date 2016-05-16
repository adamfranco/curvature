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
