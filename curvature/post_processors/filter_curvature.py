# -*- coding: UTF-8 -*-
import argparse

class FilterCurvature(object):
	def __init__(self, min=None, max=None):
		self.min = min
		self.max = max

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Filter out items not meeting our curvature levels.')
		parser.add_argument('--min', type=float, default=None, help='The minimum curvature level to be included in the output, e.g. 300')
		parser.add_argument('--max', type=float, default=None, help='The maximum curvature level to be included in the output, e.g. 5000')
		args = parser.parse_args(argv)
		return cls(args.min, args.max)

	def process(self, iterable):
		for item in iterable:
			if self.min is not None:
				if item['curvature'] < self.min:
					continue
			if self.max is not None:
				if item['curvature'] > self.max:
					continue
			yield(item)
