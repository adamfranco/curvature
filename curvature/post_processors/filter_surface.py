# -*- coding: UTF-8 -*-
import argparse
import itertools

class FilterSurface(object):
  def __init__(self, include_surfaces=None, exclude_surfaces=None):
    if (include_surfaces is not None and exclude_surfaces is not None):
      raise RuntimeError("Error: conficting parameters, please pick only one ruleset")
    if (include_surfaces is not None):
      self.filter = lambda item: 'surface' in item and item['surface'].split(';')[0] in include_surfaces
    elif (exclude_surfaces is not None):
      self.filter = lambda item: 'surface' not in item or item['surface'].split(';')[0] not in exclude_surfaces
    else:
      self.filter = lambda item: True

  @classmethod
  def parse(cls, argv):
    parser = argparse.ArgumentParser(description='Filter paths curve surface')
    parser.add_argument('--include_surfaces', type=str, default='', dest='include_surfaces', help='A comma separated list of specific surfaces to include')
    parser.add_argument('--exclude_surfaces', type=str, default='', dest='exclude_surfaces', help='A comma separated list of specific surfaces to include')
    args = parser.parse_args(argv)
    include_surfaces = filter(None,args.include_surfaces.split(','))
    exclude_surfaces = filter(None,args.exclude_surfaces.split(','))
    return cls(include_surfaces=include_surfaces, exclude_surfaces=exclude_surfaces)

  def select(item):
    surface = item['surface'].split(';')[0]
    if (self.include_surfaces is not None and surface in self.include_surfaces):
      return True
    elif (self.exclude_surfaces is not None and surface not in self.exclude_surfaces):
      return True
    return False

  def process(self, iterable):
    return itertools.ifilter(self.filter, iterable)
      