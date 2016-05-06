class AddPoints(object):
	@classmethod
	def parse(cls, argv):
		return cls()
	def process(self, iterable):
		for item in iterable:
			segments = item['segments']
			# Add the starting point from the first segment.
			points = [(segments[0]['start'][1], segments[0]['start'][0])]
			# Add the ending point from all segments.
			for segment in segments:
					points.append((segment['end'][1], segment['end'][0]))
			item['points'] = points
			yield(item)

