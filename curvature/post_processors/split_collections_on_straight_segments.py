# -*- coding: UTF-8 -*-
import argparse
from copy import copy
from curvature.collection_tools import CollectionSplitter

class SplitCollectionsOnStraightSegments(CollectionSplitter):

    # sequences of straight segments longer than this (in meters) will cause a way
    # to be split into multiple sections. If 0, ways will not be split.
    # 2414 meters ~= 1.5 miles, 1609 ~= 1 mile
    straight_segment_split_threshold = 2414

    def __init__(self, straight_segment_split_threshold=2414):
        self.straight_segment_split_threshold = straight_segment_split_threshold

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='split_collections_on_straight_segments', description='Sequences of straight segments longer than the length passed (in meters) will cause a collection of ways to be split into multiple collections.')
        parser.add_argument('--length', type=int, default=2414, help='The minimum length of straight-segments to split on. Defaults is 2414 meters ~= 1.5 miles. 1609 meters ~= 1 mile')
        args = parser.parse_args(argv)
        if args.length < 1:
            raise argparse.ArgumentTypeError("--length must be an integer greater than 0.")
        return cls(args.length)

    def process(self, iterable):
        for collection in iterable:
            result_collection = self.create_result_collection(collection)
            straight_buffer = []
            straight_distance = 0

            for way in collection['ways']:
                for segment_index, segment in enumerate(way['segments']):
                    # Split the collection if we've hit the first curve after
                    # a long straight segment.
                    if segment['curvature_level'] and straight_distance > self.straight_segment_split_threshold:
                        if len(result_collection['ways']):
                            yield(result_collection)
                            result_collection = self.create_result_collection(collection)
                        straight_collection = self.create_result_collection(collection)
                        straight_collection['ways'] = straight_buffer
                        yield(straight_collection)
                        straight_buffer = []
                        straight_distance = 0

                    # Reset the straight distance if we have a significant curve.
                    if segment['curvature_level']:
                        # If we have buffered straight segments, add them back to our result_collection
                        if len(straight_buffer):
                            self.copy_buffer(straight_buffer, result_collection['ways'])
                            straight_buffer = []

                        straight_distance = 0
                        self.buffer_way_segment(way, segment_index, result_collection['ways'])
                    # Add to our straight distance and buffer our segments
                    else:
                        straight_distance += segment['length']
                        self.buffer_way_segment(way, segment_index, straight_buffer)

            # Yield and trailing straight buffer long enough.
            if len(straight_buffer) and straight_distance > self.straight_segment_split_threshold:
                # Yield the remaining collection.
                if len(result_collection['ways']):
                    yield(result_collection)
                    result_collection = self.create_result_collection(collection)
                straight_collection = self.create_result_collection(collection)
                straight_collection['ways'] = straight_buffer
                yield(straight_collection)
                straight_buffer = []
                straight_distance = 0
            # Otherwise, unbuffer any trailing straight buffer onto the end of the result collection
            else:
                if len(straight_buffer):
                    self.copy_buffer(straight_buffer, result_collection['ways'])
                    straight_buffer = []
                # Yield the remaining collection.
                if len(result_collection['ways']):
                    yield(result_collection)

    # Add a slice of a way including the segment, coords, refs that match a segment to a buffer.
    def buffer_way_segment(self, way, segment_index, buffer):
        # See if the last way in the buffer has the same id. If not, add a copy of our way.
        if not len(buffer) or buffer[-1]['id'] != way['id']:
            way_copy = copy(way)
            way_copy['refs'] = []
            way_copy['coords'] = []
            way_copy['segments'] = []
            buffer.append(way_copy)

        self.append_way_data(buffer[-1], way, segment_index)

    def append_way_data(self, dest_way, source_way, source_segment_index):
        # Add the slice of data from our way.
        dest_way['segments'].append(source_way['segments'][source_segment_index])
        # Add the first point if we are at the beginning of the way since the number of these will always be one more than our number of segments
        if not len(dest_way['refs']):
            dest_way['refs'].append(source_way['refs'][source_segment_index])
        if not len(dest_way['coords']):
            dest_way['coords'].append(source_way['coords'][source_segment_index])
        # Add our second point associated with the segment
        dest_way['refs'].append(source_way['refs'][source_segment_index + 1])
        dest_way['coords'].append(source_way['coords'][source_segment_index + 1])

    # Copy the contents of one buffer into another, merging segments, coords, and refs.
    def copy_buffer(self, source_buffer, destination_buffer):
        # There's nothing to do if we have an empty source buffer.
        if not len(source_buffer):
            return

        # if the first way in the source buffer has the same id as the last way in
        # the destination buffer, merge them into a single way.
        if len(destination_buffer) and source_buffer[0]['id'] == destination_buffer[-1]['id']:
            way = source_buffer.pop(0)
            for i in range(0, len(way['segments'])):
                self.append_way_data(destination_buffer[-1], way, i)

        # Just copy the rest of the ways into the destination.
        for way in source_buffer:
            destination_buffer.append(way)
