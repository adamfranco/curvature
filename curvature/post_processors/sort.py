# -*- coding: UTF-8 -*-
import argparse
class Sort(object):
	def __init__(self, key, reverse=False):
		self.reverse = reverse
		self.key = key

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Sort items in the stream')
		parser.add_argument('--key', type=str, default='curvature', help='The key to sort on, default: curvature')
		parser.add_argument('--direction', type=str, default='DESC', help='The sort direction, ASC or DESC. Default: DESC')
		args = parser.parse_args(argv)
		if args.direction == 'ASC':
			reverse = False
		elif args.direction == 'DESC':
			reverse = True
		else:
			raise RuntimeError("\n--direction must be ASC or DESC.")

		return cls(args.key, reverse)

	def process(self, iterable):
		items = sorted(iterable, key=lambda k: k[self.key], reverse=self.reverse)
		for item in items:
			yield(item)