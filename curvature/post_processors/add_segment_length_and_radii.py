# -*- coding: UTF-8 -*-
import math
from curvature.geomath import distance_on_earth

class AddSegmentLengthAndRadii(object):

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            all_segments = []
            for way in collection:
                if 'segments' not in way:
                    raise ValueError('Required "segments" not found in way. Add them with `curvature-pp add_segments` before using this processor.')
                all_segments = all_segments + way['segments']
            self.calculate_segment_radii(all_segments)
            yield(collection)

    def calculate_segment_radii(self, segments):
        # Special case: If only one segment, just use a static large 'straight'
        # radius, there is no curve.
        if len(segments) == 1:
            segments[0]['radius'] = 1000000

        i = 0
        while i < len(segments):
            first_segment = segments[i]
            i = i + 1
            if 'length' not in first_segment:
                first_segment['length'] = distance_on_earth(first_segment['start'][0],
                                                            first_segment['start'][1],
                                                            first_segment['end'][0],
                                                            first_segment['end'][1] )

            if i < len(segments):
                second_segment = segments[i]
                if 'length' not in second_segment:
                    second_segment['length'] = distance_on_earth(second_segment['start'][0],
                                                                second_segment['start'][1],
                                                                second_segment['end'][0],
                                                                second_segment['end'][1] )
            else:
                second_segment = None

            if second_segment:
                base_length = distance_on_earth(first_segment['start'][0],
                                                first_segment['start'][1],
                                                second_segment['end'][0],
                                                second_segment['end'][1] )
            else:
                base_length = None

            # ignore curvature from zero-distance
            if first_segment['length'] > 0 and second_segment and second_segment['length'] > 0 and base_length > 0:
                # Circumcircle radius calculation from http://www.mathopenref.com/trianglecircumcircle.html
                a = first_segment['length']
                b = second_segment['length']
                c = base_length
                r = (a * b * c)/math.sqrt(math.fabs((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)))
            else:
                r = 1000000

            # The first segment only is part of one triangle, so just use that radius.
            # Note that 1 is the first segment since we've already incremented i above.
            if i == 1:
                first_segment['radius'] = r
            # Otherwise, set the radius of the previous segment to the smaller radius of the two circumcircles it's a part of.
            # An alternative implementation would be to average the radii or do some sort
            # of weighted average, but I think I chose to use the shorter radius as curves
            # are often followed by long straight-aways, and this method seemed to work well
            # with the data.
            else:
                if first_segment['radius'] > r:
                    first_segment['radius'] = r

            # If there is a second segment, set its initial radius to that of this first triangle.
            if second_segment:
                second_segment['radius'] = r
