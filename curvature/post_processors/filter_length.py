# -*- coding: UTF-8 -*-
import argparse

class FilterLength(object):
	def __init__(self, min=None, max=None):
		self.min = min
		self.max = max

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Filter out items not meeting our length levels.')
		parser.add_argument('--min', type=float, default=None, help='The minimum length level to be included in the output, e.g. 300, default 0 means no minum')
		parser.add_argument('--max', type=float, default=None, help='The maximum length level to be included in the output, e.g. 5000, default 0 means no maximum')
		args = parser.parse_args(argv)
		return cls(args.min, args.max)

	def process(self, iterable):
		for item in iterable:
			if self.min is not None:
				if item['length'] < self.min:
					continue
			if self.max is not None:
				if item['length'] > self.max:
					continue
			yield(item)
