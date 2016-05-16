# -*- coding: UTF-8 -*-
import math
from curvature.geomath import distance_on_earth

class FilterSegmentDeflections(object):

    level_1_max_radius = 175
    keep_eliminated = False

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            all_segments = []
            for way in collection['ways']:
                if 'segments' not in way:
                    raise ValueError('Required "segments" not found in way. Add them with `curvature-pp add_segments` before using this processor.')
                all_segments = all_segments + way['segments']

            self.filter_deflections(all_segments)
            yield(collection)

    def filter_deflections(self, segments):
        for i, segment in enumerate(segments):
            # While we are in straight segments, be wary of single-point (two-segment)
            # deflections from our straight line if the next two segments are followed
            # by a straight section. E.g. __/\__
            # We want to differentiate a jog off of an otherwise straight line from a
            # curve between two straight sections like these:
            #     __ __    __
            #   /        /   \
            self.filter_deflection_of_straight_segments(segments, i, 3)

            # While we are in straight segments, be wary of two/three-point (three/four-segment)
            # deflections from our straight line if the next two segments are followed
            # by a straight section. E.g. __/\ _   __
            #                                   \/
            # We want to differentiate a jog off of an otherwise straight line from a
            # curve between two straight sections like these:
            #     __ __    __
            #   /        /   \
            self.filter_deflection_of_straight_segments(segments, i, 4)
            self.filter_deflection_of_straight_segments(segments, i, 5)
            # Note: Because the curvature calculation currently uses the shorter
            # radius of the two triangles for each segment, this causes curves to
            # slightly "bleed" into straighter segments. We need to check two more
            # segments ahead.
            self.filter_deflection_of_straight_segments(segments, i, 6)
            self.filter_deflection_of_straight_segments(segments, i, 7)

    def filter_deflection_of_straight_segments(self, segments, start_index, look_ahead):
        if look_ahead < 3:
            raise ValueError("look_ahead must be 3 or more")
        try:
            first_straight = segments[start_index]
            next_straight = segments[start_index + look_ahead]
            # if (first_straight['curvature_level'] and not 'curvature_filtered' in first_straight) or (next_straight['curvature_level'] and not 'curvature_filtered' in next_straight):
            if (first_straight['curvature_level'] and not 'curvature_filtered' in first_straight) or (next_straight['curvature_level'] and not 'curvature_filtered' in next_straight):
                return
            heading_a = self.get_segment_heading(first_straight)
            heading_b = self.get_segment_heading(next_straight)
            heading_diff = abs(heading_a - heading_b)
            # Compare the difference in heading to the angle that wold be expected
            # for a curve just barely meeting our threshold for straight/curved.
            gap_distance = distance_on_earth(first_straight['end'][0], first_straight['end'][1], next_straight['start'][0], next_straight['start'][1])
            min_variance = gap_distance / self.level_1_max_radius
            if abs(heading_diff) < min_variance:
                # Mark them as curvature_filtered so that we can show them in the output
                for i in range(start_index, start_index + look_ahead):
                    if segments[i]['curvature_level']:
                        segments[i]['curvature_filtered'] = True
                if not self.keep_eliminated:
                    # unset the curvature level of the intermediate segments
                    for i in range(start_index, start_index + look_ahead):
                        segments[i]['curvature_level'] = 0
                        segments[i]['curvature'] = 0
        except IndexError:
            return

    def get_segment_heading(self, segment):
        return 180 + math.atan2((segment['end'][0] - segment['start'][0]),(segment['end'][1] - segment['start'][1])) * (180 / math.pi)

    def heading_diff(self, initial, final):
        if initial > 360 or initial < 0 or final > 360 or final < 0:
            raise ValueError("Initial or final headings are out of bounds, must be 0-360")

        diff = final - initial
        absDiff = abs(diff)

        if absDiff <= 180:
            if absDiff == 180:
                return absDiff
            else:
                return diff
        elif final > initial:
            return absDiff - 360
        else:
            return 360 - absDiff
