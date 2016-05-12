# -*- coding: UTF-8 -*-
class AddLength(object):
	@classmethod
	def parse(cls, argv):
		return cls()

	def process(self, iterable):
		for collection in iterable:
			for item in collection:
				segments = item['segments']
				sum = 0
				for segment in segments:
						sum += segment['length']
				item['length'] = sum
			yield(collection)
