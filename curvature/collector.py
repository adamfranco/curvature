import sys
import math
import resource
from imposm.parser import OSMParser
rad_earth_m = 6373000 # Radius of the earth in meters

# simple class that handles the parsed OSM data.
class WayCollector(object):
	ways = []
	coords = {}
	num_coords = 0
	num_ways = 0
	
	verbose = False
	min_lat_bound = None
	max_lat_bound = None
	min_lon_bound = None
	max_lon_bound = None
	
	roads = 'secondary', 'residential', 'tertiary', 'primary', 'primary_link', 'motorway', 'motorway_link', 'road', 'trunk', 'trunk_link', 'unclassified'
	ignored_surfaces = 'dirt', 'unpaved', 'gravel', 'sand', 'grass', 'ground'
	level_1_max_radius = 175
	level_1_weight = 1
	level_2_max_radius = 100
	level_2_weight = 1.3
	level_3_max_radius = 60
	level_3_weight = 1.6
	level_4_max_radius = 30
	level_4_weight = 2
	
	def load_file(self, filename):
		# Reinitialize if we have a new file
		ways = []
		coords = {}
		num_coords = 0
		num_ways = 0
		
		# status output
		if self.verbose:
			sys.stderr.write("loading ways, each '-' is 100 ways, each row is 10,000 ways\n")
		
		p = OSMParser(ways_callback=self.ways_callback)
		p.parse(filename)
		
		# status output
		if self.verbose:
			sys.stderr.write("\n{} ways matched in {} {mem:.1f}MB memory used, {} coordinates will be loaded, each '.' is 1% complete\n".format(len(self.ways), filename, len(self.coords), mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
			
			total = len(self.coords)
			if total < 100:
				self.coords_marker = 1
			else:
				self.coords_marker = round(total/100)
		
		p = OSMParser(coords_callback=self.coords_callback)
		p.parse(filename)
		
		# status output
		if self.verbose:
			sys.stderr.write("\ncoordinates loaded {mem:.1f}MB memory used, calculating curvature, each '.' is 1% complete\n".format(mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
			sys.stderr.flush()
		
		# Loop through the ways and calculate their curvature
		self.calculate()
		
		# status output
		if self.verbose:
			sys.stderr.write("calculation complete, {mem:.1f}MB memory used\n".format(mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
			sys.stderr.flush()
	
	def coords_callback(self, coords):
		# callback method for coords
		for osm_id, lon, lat in coords:
			if self.min_lat_bound and lat < self.min_lat_bound:
				continue
			if self.max_lat_bound and lat > self.max_lat_bound:
				continue
			if self.min_lon_bound and lon < self.min_lon_bound:
				continue
			if self.max_lon_bound and lon > self.max_lon_bound:
				continue
			
			if osm_id in self.coords:
				self.coords[osm_id] = (lat, lon)
			
				# status output
				if self.verbose:
					self.num_coords = self.num_coords + 1
					if not (self.num_coords % self.coords_marker):
						sys.stderr.write('.')
						sys.stderr.flush()

	def ways_callback(self, ways):
		# callback method for ways
		for osmid, tags, refs in ways:
			if refs[0] == refs[-1]:
				continue
			
			if self.min_lat_bound or self.max_lat_bound or self.min_lon_bound or self.min_lat_bound:
				try:
					start = self.coords[refs[0]]
					if self.min_lat_bound and start[0] < self.min_lat_bound:
						continue
					if self.max_lat_bound and start[0] > self.max_lat_bound:
						continue
					if self.min_lon_bound and start[1] < self.min_lon_bound:
						continue
					if self.max_lon_bound and start[1] > self.max_lon_bound:
						continue
				except:
					continue
			
			if 'name' not in tags or tags['name'] == '':
				continue
			if 'surface' in tags and tags['surface'] in self.ignored_surfaces:
				continue
			if 'highway' in tags and tags['highway'] in self.roads:
				way = {'id': osmid, 'type': tags['highway'], 'name':tags['name'], 'refs': refs}
				if 'tiger:county' in tags:
					way['county'] = tags['tiger:county']
				else:
					way['county'] = ''
				if 'surface' in tags:
					way['surface'] = tags['surface']
				else:
					way['surface'] = 'unknown'
				self.ways.append(way)
				
				for ref in refs:
					self.coords[ref] = None
			
				# status output
				if self.verbose:
					self.num_ways = self.num_ways + 1
					if not (self.num_ways % 100):
						sys.stderr.write('-')
						if not self.num_ways % 10000:
							sys.stderr.write('\n')
						sys.stderr.flush()
	
	def calculate(self):
		# status output
		if self.verbose:
			i = 0
			total = len(self.ways)
			if total < 100:
				marker = 1
			else:
				marker = round(total/100)
		
		for way in self.ways:
			# status output
			if self.verbose:
				i = i + 1
				if not (i % marker):
					sys.stderr.write('.')
					sys.stderr.flush()
			
			try:
				self.calculate_distance_and_curvature(way)
			except:
				continue
		
		# status output
		if self.verbose:
			sys.stderr.write('\n')
	
	def calculate_distance_and_curvature(self, way):
		way['distance'] = 0.0
		way['curvature'] = 0.0
		way['length'] = 0.0
		start = self.coords[way['refs'][0]]
		end = self.coords[way['refs'][-1]]
		way['distance'] = distance_on_unit_sphere(start[0], start[1], end[0], end[1]) * rad_earth_m
		second = 0
		third = 0
		segments = []
		for ref in way['refs']:
			first = self.coords[ref]
			
			if not second:
				second = first
				continue
			
			first_second_length = distance_on_unit_sphere(first[0], first[1], second[0], second[1]) * rad_earth_m
			way['length'] += first_second_length
			
			if not third:
				third = second
				second = first
				second_third_length = first_second_length
				continue
			
			first_third_length = distance_on_unit_sphere(first[0], first[1], third[0], third[1]) * rad_earth_m
			# ignore curvature from zero-distance
			if first_third_length > 0 and first_second_length > 0 and second_third_length > 0:
				# Circumcircle radius calculation from http://www.mathopenref.com/trianglecircumcircle.html
				a = first_second_length
				b = second_third_length
				c = first_third_length
				r = (a * b * c)/math.sqrt(math.fabs((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)))
			else:
				r = 1000
			
			if not len(segments):
				# Add the first segment using the first point
				segments.append({'start': third, 'end': second, 'length': second_third_length, 'radius': r})
			else:
				# set the radius of the previous segment to the smaller radius of the two circumcircles it's a part of
				if segments[-1]['radius'] > r:
					segments[-1]['radius'] = r
			# Add our latest segment
			segments.append({'start': second, 'end': first, 'length': first_second_length, 'radius': r})
			
			third = second
			second = first
			second_third_length = first_second_length
		
		way['segments'] = segments

		# Calculate the curvature as a weighted distance traveled at each curvature.
		way['curvature'] = 0
		for segment in segments:
			if segment['radius'] < self.level_4_max_radius:
				segment['curvature_level'] = 4
				way['curvature'] += segment['length'] * self.level_4_weight
			elif segment['radius'] < self.level_3_max_radius:
				segment['curvature_level'] = 3
				way['curvature'] += segment['length'] * self.level_3_weight
			elif segment['radius'] < self.level_2_max_radius:
				segment['curvature_level'] = 2
				way['curvature'] += segment['length'] * self.level_2_weight
			elif segment['radius'] < self.level_1_max_radius:
				segment['curvature_level'] = 1
				way['curvature'] += segment['length'] * self.level_1_weight
			else:
				segment['curvature_level'] = 0
				

# From http://www.johndcook.com/python_longitude_latitude.html
def distance_on_unit_sphere(lat1, long1, lat2, long2):
	if lat1 == lat2	 and long1 == long2:
		return 0

	# Convert latitude and longitude to 
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0
		
	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians
		
	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians
		
	# Compute spherical distance from spherical coordinates.
		
	# For two locations in spherical coordinates 
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) = 
	#	 sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length
	
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
		   math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )

	# Remember to multiply arc by the radius of the earth 
	# in your favorite set of units to get length.
	return arc