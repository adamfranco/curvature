# -*- coding: UTF-8 -*-
import argparse

class FilterNumConstituents(object):
	def __init__(self, min=None, max=None):
		self.min = min
		self.max = max

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Filter out items not meeting our curvature levels.')
		parser.add_argument('--min', type=int, default=0, help='The minimum number of constituents a collection may have. Default is 0, no-min.')
		parser.add_argument('--max', type=int, default=0, help='The minimum number of constituents a collection may have. Default is 0, no-max.')
		args = parser.parse_args(argv)
		return cls(args.min, args.max)

	def process(self, iterable):
		for item in iterable:
			if self.min > 0:
				if len(item) < self.min:
					continue
			if self.max > 0:
				if len(item) > self.max:
					continue
			yield(item)
