#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import codecs
import msgpack
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from curvature.post_processors.filter_out_ways_with_tag import FilterOutWaysWithTag
from curvature.post_processors.add_segments import AddSegments
from curvature.post_processors.add_segment_length_and_radius import AddSegmentLengthAndRadius
from curvature.post_processors.add_segment_curvature import AddSegmentCurvature
from curvature.post_processors.filter_segment_deflections import FilterSegmentDeflections
from curvature.post_processors.split_collections_on_straight_segments import SplitCollectionsOnStraightSegments
from curvature.post_processors.roll_up_length import RollUpLength
from curvature.post_processors.roll_up_curvature import RollUpCurvature
from curvature.post_processors.filter_collections_by_curvature import FilterCollectionsByCurvature
from curvature.post_processors.sort_collections_by_sum import SortCollectionsBySum

# Set our output to default to UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')
# sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

class CallbackedProcessor(object):
  def __init__(self, processor, callback):
    self.processor = processor
    self.callback = callback

  def input(self, arg):
    # Since processors do not have a process_item interface we are mocking it for now
    for output in self.processor.process([arg]):
      self.callback(output)


# Take the following processing steps first:
# 1. Collect the highway ways and their points into collections.
# 2. Filter out unpaved ways and highway types we aren't interested in.
# 3. Add segments and their lengths & radii.
# 4. Calculate the curvature and filter curvature values for "deflections" (noisy data)
# 5. Split our collections on long straight-aways (longer than 1.5 miles) to avoid
#    highlighting long straight roads with infrequent curvy-sections.
# 6. Sum the length and curvature of the sections in each way for reuse.
# 7. Filter out collections not meeting our minimum curvature thresholds.
# 3. Sort the items by their curvature value.
# 3. Save the intermediate data.


chain = [
  FilterOutWaysWithTag('surface', ['unpaved','dirt','gravel','fine_gravel','sand','grass','ground','pebblestone','mud','clay','dirt/sand','soil']),
  FilterOutWaysWithTag('service', ['driveway', 'parking_aisle', 'drive-through', 'parking', 'bus', 'emergency_access']),
  AddSegments(),
  AddSegmentLengthAndRadius(),
  AddSegmentCurvature(),
  FilterSegmentDeflections(),
  SplitCollectionsOnStraightSegments(2414),
  RollUpLength(),
  RollUpCurvature(),
  FilterCollectionsByCurvature(min=300),
  SortCollectionsBySum(key='curvature', reverse=True)
]

def print_msgpack(arg):
  sys.stdout.write(msgpack.packb(arg))

prev_callback = print_msgpack

for processor in reversed(chain):
  prev_callback = CallbackedProcessor(processor, prev_callback).input

for collection in msgpack.Unpacker(sys.stdin, use_list=True):
  prev_callback(collection)
