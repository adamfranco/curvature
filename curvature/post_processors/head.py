# -*- coding: UTF-8 -*-
import argparse
class Head(object):
	def __init__(self, num):
		self.num = num

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Return only the n first items')
		parser.add_argument('-n', type=int, default=None, help='The number of items to forward')
		args = parser.parse_args(argv)
		if args.n is None:
			raise RuntimeError("\n-n must be supplied")
		return cls(args.n)

	def process(self, iterable):
		idx = 0
		for item in iterable:
			if idx >= self.num:
				break
			yield(item)
			idx += 1