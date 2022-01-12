
class CollectionSplitter(object):

    def create_result_collection(self, collection):
      result_collection = dict((key,value) for key, value in collection.items() if key != 'ways')
      result_collection['ways'] = []
      return result_collection

# Abstract class for post-processors that traverse segments, squashing curvature.
class SquashCurvatureNearbyProcessorAbstract(object):
    def __init__(self, distance=0):
        self.distance = distance

    def process(self, iterable):
        for collection in iterable:
            yield(self.process_collection(collection))

    # Squash curvature values near an initial point out to our configured distance.
    def squash_segment_curvature_nearby(self, collection, initial_way_index, initial_segment_index, initial_segment_end):
        segments = CollectionSegmentTraverser(collection, initial_way_index, initial_segment_index)
        # The initial matching segment will always have its curvature squashed.
        initial_segment = segments.next()
        self.squash_segment_curvature(initial_segment)

        # Explore forward, squashing curvature until our distance has been exceeded.
        if initial_segment_end == 'start':
            d = initial_segment['length']
        else:
            d = 0
        while d < self.distance and segments.has_next():
            segment = segments.next()
            self.squash_segment_curvature(segment)
            d = d + segment['length']

        # Explore backward, squashing curvature until our distance has been exceeded.
        segments.reset_postition()
        segments.set_direction('backward')
        segments.next() # We've already squashed the initial segment's curvature.
        if initial_segment_end == 'end':
            d = initial_segment['length']
        else:
            d = 0
        while d < self.distance and segments.has_next():
            segment = segments.next()
            self.squash_segment_curvature(segment)
            d = d + segment['length']

    # Squash the curvature values on a single segment.
    def squash_segment_curvature(self, segment):
        if 'curvature' in segment.keys():
            segment['curvature'] = 0
        if 'curvature_level' in segment.keys():
            segment['curvature_level'] = 0

# Abstract class for post-processors that traverse segments, inflating curvature.
class InflateCurvatureNearbyProcessorAbstract(object):
    def __init__(self, curvature=1, distance=0):
        self.curvature = curvature
        self.distance = distance

    def process(self, iterable):
        for collection in iterable:
            yield(self.process_collection(collection))

    # Inflate curvature values near an initial point out to our configured distance.
    def inflate_segment_curvature_nearby(self, collection, initial_way_index, initial_segment_index, initial_segment_end):
        segments = CollectionSegmentTraverser(collection, initial_way_index, initial_segment_index)
        # The initial matching segment will always have its curvature inflated.
        initial_segment = segments.next()
        self.inflate_segment_curvature(initial_segment)

        # Explore forward, inflating curvature until our distance has been exceeded.
        if initial_segment_end == 'start':
            d = initial_segment['length']
        else:
            d = 0
        while d < self.distance and segments.has_next():
            segment = segments.next()
            self.inflate_segment_curvature(segment)
            d = d + segment['length']

        # Explore backward, inflating curvature until our distance has been exceeded.
        segments.reset_postition()
        segments.set_direction('backward')
        segments.next() # We've already inflated the initial segment's curvature.
        if initial_segment_end == 'end':
            d = initial_segment['length']
        else:
            d = 0
        while d < self.distance and segments.has_next():
            segment = segments.next()
            self.inflate_segment_curvature(segment)
            d = d + segment['length']

    # Inflate the curvature values on a single segment.
    def inflate_segment_curvature(self, segment):
        if 'curvature' in segment.keys():
            segment['curvature'] = segment['curvature'] + self.curvature
        else:
            segment['curvature'] = self.curvature
        if 'curvature_level' in segment.keys() and segment['curvature_level'] < 4:
            segment['curvature_level'] = segment['curvature_level'] + 1

# Utility class for traversing through adjoining segments in a collection.
class CollectionSegmentTraverser(object):

    def __init__(self, collection, way_index=0, segment_index=0, direction='forward'):
        self.collection = collection
        self.way_index = way_index
        self.initial_way_index = way_index
        self.segment_index = segment_index
        self.initial_segment_index = segment_index
        if direction != 'forward' and direction != 'backward':
            raise ValueError("direction must be 'forward' or 'backward'.")
        self.direction = direction
        self.initial_direction = direction

    def set_direction(self, direction):
        if direction != 'forward' and direction != 'backward':
            raise ValueError("direction must be 'forward' or 'backward'.")
        self.direction = direction

    def reset_direction(self):
        self.direction = self.initial_direction

    def set_postition(self, way_index=0, segment_index=0):
        self.way_index = way_index
        self.segment_index = segment_index

    def reset_postition(self):
        self.way_index = self.initial_way_index
        self.segment_index = self.initial_segment_index

    def has_next(self):
        if self.way_index < 0 or self.way_index >= len(self.collection['ways']):
            return False
        if self.segment_index < 0 or self.segment_index >= len(self.collection['ways'][self.way_index]['segments']):
            return False
        return True

    def current(self):
        return self.collection['ways'][self.way_index]['segments'][self.segment_index]

    def next(self):
        segment = self.current()
        self.advance_postion()
        return segment

    def advance_postion(self):
        if self.direction == 'backward':
            self.advance_postion_backward()
        else:
            self.advance_postion_forward()

    def advance_postion_forward(self):
        # Try to increment the segment index first if possible.
        if self.segment_index < (len(self.collection['ways'][self.way_index]['segments']) - 1):
            self.segment_index = self.segment_index + 1
        # Shift to the beginning of the next way.
        else:
            self.segment_index = 0
            self.way_index = self.way_index + 1

    def advance_postion_backward(self):
        # Try to decrement the segment index first if possible.
        if self.segment_index > 0:
            self.segment_index = self.segment_index - 1
        # Shift to the end of the next way.
        else:
            self.way_index = self.way_index - 1
            # Set to the last segment if we are on a valid way.
            if self.way_index >= 0:
                self.segment_index = len(self.collection['ways'][self.way_index]['segments']) - 1
            else:
                self.segment_index = 0
