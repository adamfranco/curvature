# -*- coding: UTF-8 -*-
import math
from curvature.geomath import distance_on_earth
from curvature.radiusmath import circum_circle_radius
import itertools

class AddSegmentLengthAndRadius(object):
    MAX_RADIUS = 10000

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            if 'segments' not in collection['ways'][0]:
                raise ValueError('Required "segments" not found in way. Add them with `curvature-pp add_segments` before using this processor.')
            all_segments = list(itertools.chain(*map(lambda way: way['segments'], collection['ways'])))
            self.calculate_length(all_segments)
            self.calculate_segment_radii(all_segments)
            yield(collection)

    def calculate_length(self, segments):
        for segment in segments:
            segment['length'] = distance_on_earth(
                segment['start'][0],
                segment['start'][1],
                segment['end'][0],
                segment['end'][1]
            )

    def calculate_segment_radii(self, segments):
        # Special case: If only one segment, just use a static large 'straight'
        # radius, there is no curve.
        if len(segments) == 1:
            segments[0]['radius'] = AddSegmentLengthAndRadius.MAX_RADIUS

        for i, segment in enumerate(segments):
            next_index = i + 1
            if next_index < len(segments):
                next_segment = segments[next_index]
                base_length = distance_on_earth(segment['start'][0],
                                                segment['start'][1],
                                                next_segment['end'][0],
                                                next_segment['end'][1])
                radius = circum_circle_radius(segment['length'], next_segment['length'], base_length)
                # The first segment only is part of one triangle, so just use that radius.
                # Note that 1 is the first segment since we've already incremented i above.
                # Otherwise, set the radius of the previous segment to the smaller radius of the two circumcircles it's a part of.
                # An alternative implementation would be to average the radii or do some sort
                # of weighted average, but I think I chose to use the shorter radius as curves
                # are often followed by long straight-aways, and this method seemed to work well
                # with the data.
                if i == 0:
                    segment['radius'] = radius
                elif segment['radius'] > radius:
                    segment['radius'] = radius
                next_segment['radius'] = radius
            else:
                if segment['radius'] > AddSegmentLengthAndRadius.MAX_RADIUS:
                    segment['radius'] = AddSegmentLengthAndRadius.MAX_RADIUS
