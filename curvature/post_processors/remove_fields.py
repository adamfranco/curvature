# -*- coding: UTF-8 -*-
import argparse

class RemoveFields(object):
	def __init__(self, fields):
		self.fields = fields

	@classmethod
	def parse(cls, argv):
		parser = argparse.ArgumentParser(description='Strip certain fields from the data.')
		parser.add_argument('--fields', type=str, help='A comma-separated list of the field-keys to strip. Example --fields sections,county')
		args = parser.parse_args(argv)
		if not args.fields:
			raise RuntimeError("Error:   --fields must be specified and contain at least 1 field.\n")
		to_strip = args.fields.split(',')
		return cls(to_strip)

	def process(self, iterable):
		for item in iterable:
			for field in self.fields:
					if field in item:
							del item[field]
			yield(item)
