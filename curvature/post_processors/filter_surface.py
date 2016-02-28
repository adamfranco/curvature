# -*- coding: UTF-8 -*-
import argparse

class FilterSurface(object):
  def __init__(self, include_surfaces=None, exclude_surfaces=None):
    self.include_surfaces = include_surfaces
    self.exclude_surfaces = exclude_surfaces

  @classmethod
  def parse(cls, argv):
    parser = argparse.ArgumentParser(description='Filter paths curve surface')
    parser.add_argument('--include_surfaces', type=str, default='', dest='include_surfaces', help='A comma separated list of specific surfaces to include')
    parser.add_argument('--exclude_surfaces', type=str, default='', dest='exclude_surfaces', help='A comma separated list of specific surfaces to include')
    args = parser.parse_args(argv)
    include_surfaces = filter(None,args.include_surfaces.split(','))
    exclude_surfaces = filter(None,args.exclude_surfaces.split(','))
    if (len(include_surfaces) > 0 and len(exclude_surfaces) > 0):
      raise RuntimeError("Error: conficting parameters, please pick only one ruleset")
    if (len(include_surfaces) > 0):
      return cls(include_surfaces=include_surfaces)
    else:
      return cls(exclude_surfaces=exclude_surfaces)

  def process(self, iterable):
    for item in iterable:
      surface = item['surface'].split(';')[0]
      if (self.include_surfaces is not None and surface in self.include_surfaces):
        yield(item)
      elif (self.exclude_surfaces is not None and surface not in self.exclude_surfaces):
        yield(item)