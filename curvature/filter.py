
class WayFilter(object):
	min_curvature = 0
	max_curvature = 0
	min_length = 0
	max_length = 0
	
	def filter(self, ways):
		if self.min_length > 0:
			ways = filter(lambda w: w['length'] / 1609 > self.min_length, ways)
		if self.max_length > 0:
			ways = filter(lambda w: w['length'] / 1609 < self.max_length, ways)
		if self.min_curvature > 0:
			ways = filter(lambda w: w['curvature'] > self.min_curvature, ways)
		if self.max_curvature > 0:
			ways = filter(lambda w: w['curvature'] < self.max_curvature, ways)
		return ways
		
	