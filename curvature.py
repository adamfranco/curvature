from imposm.parser import OSMParser

# simple class that handles the parsed OSM data.
class CurvatureEvaluator(object):
	ways = []
	roads = ['secondary', 'residential', 'tertiary', 'primary', 'primary_link', 'motorway', 'motorway_link', 'road', 'trunk', 'trunk_link', 'unclassified']
	coords_needed = []
	coords = {}
	
	def coords_callback(self, coords):
		# callback method for coords
		for osm_id, lon, lat in coords:
			if osm_id in self.coords_needed:
				self.coords[osm_id] = {'lon': lon, 'lat': lat}

	def ways_callback(self, ways):
		# callback method for ways
		for osmid, tags, refs in ways:
			if 'highway' in tags and tags['highway'] in self.roads:				
				if 'name' not in tags:
					continue
				if refs[0] == refs[-1]:
					continue
				
				way = {'id': osmid, 'type': tags['highway'], 'name':tags['name'], 'refs': refs}
				self.coords_needed = self.coords_needed + refs
				self.ways = self.ways + [way]
	
	def calculate(self):
		for way in self.ways:
			start = self.coords[way['refs'][0]]
			end = self.coords[way['refs'][-1]]
			way['distance'] = distance_on_unit_sphere(start['lat'], start['lon'], end['lat'], end['lon'])
			way['length'] = 0.0
			way['curvature'] = 0.0
			second = 0
			third = 0
			for ref in way['refs']:
				first = self.coords[ref]
				
				if not second:
					second = first
					continue
				
				first_second_length = distance_on_unit_sphere(first['lat'], first['lon'], second['lat'], second['lon'])
				way['length'] += first_second_length
				
				if not third:
					third = second
					second_third_length = first_second_length
					continue
				
				first_third_length = distance_on_unit_sphere(first['lat'], first['lon'], third['lat'], third['lon'])
				way['curvature'] += (first_second_length + second_third_length) / first_third_length
				
				third = second
				second = first
				second_third_length = first_second_length
					
					
				

# From http://www.johndcook.com/python_longitude_latitude.html
import math
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

# instantiate counter and parser and start parsing
evaluator = CurvatureEvaluator()
p = OSMParser(concurrency=4, ways_callback=evaluator.ways_callback)

import sys
import os.path
if len(sys.argv) < 2: 
	sys.exit("Please pass the path of an osm file.")
filename = sys.argv[1]
if not os.path.isfile(filename):
	sys.exit("File doesn't exist: %s" % (filename))

p.parse(filename)
print "%d ways matched in %s" % (len(evaluator.ways), filename)
p = OSMParser(concurrency=4, coords_callback=evaluator.coords_callback)
p.parse(filename)
print "%d coordinates loaded from %s" % (len(evaluator.coords_needed), filename)

# Loop through the ways and calculate their curvature
evaluator.calculate()
rad_earth = 3960 # Radius of the earth in miles

sorted_ways = sorted(evaluator.ways, key=lambda k: k['curvature'])
sorted_ways = filter(lambda w: w['length'] * rad_earth > 0.4 and w['name'] != '', sorted_ways)

print "Curvature	Length (mi) Distance (mi)	Id		Name"
for way in sorted_ways:
	print '%9.1f	%9.2f	%9.2f	%s	%s' % (way['curvature'], way['length'] * rad_earth, way['distance'] * rad_earth, way['id'], way['name'])