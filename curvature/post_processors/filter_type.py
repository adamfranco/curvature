# -*- coding: UTF-8 -*-
import argparse

class FilterType(object):
  def __init__(self, include_types=None, exclude_types=None):
    self.include_types = include_types
    self.exclude_types = exclude_types

  @classmethod
  def parse(cls, argv):
    parser = argparse.ArgumentParser(description='Filter paths curve type')
    parser.add_argument('--include_types', type=str, default='', dest='include_types', help='A comma separated list of specific types to include')
    parser.add_argument('--exclude_types', type=str, default='', dest='exclude_types', help='A comma separated list of specific types to include')
    args = parser.parse_args(argv)
    include_types = filter(None,args.include_types.split(','))
    exclude_types = filter(None,args.exclude_types.split(','))
    if (len(include_types) > 0 and len(exclude_types) > 0):
      raise RuntimeError("Error: conficting parameters, please pick only one ruleset")
    if (len(include_types) > 0):
      return cls(include_types=include_types)
    else:
      return cls(exclude_types=exclude_types)

  def process(self, iterable):
    for item in iterable:
      type = item['type'].split(';')[0]
      if (self.include_types is not None and type in self.include_types):
        yield(item)
      elif (self.exclude_types is not None and type not in self.exclude_types):
        yield(item)