#!/usr/bin/env python
import codecs
import sys
import os.path
import math
from imposm.parser import OSMParser
import argparse

parser = argparse.ArgumentParser(description='Find the roads that are most twisty in an OSM XML file.')
parser.add_argument('-v', action='store_true', help='verbose mode, showing status output')
parser.add_argument('-q', action='store_true', help='quiet mode, do not output tabular data')
parser.add_argument('--no_kml', action='store_true', help='if passed, no KML file will be generated. By default a KML file is generated with the name of the input file followed by .kml')
parser.add_argument('--kml_file', type=argparse.FileType('w'), help='a custom destination for the KML file')
parser.add_argument('--min_length', type=float, help='the minimum length of a way that should be included, in miles, 0 for no minimum. The default is 2.0')
parser.add_argument('--max_length', type=float, help='the maximum length of a way that should be included, in miles, 0 for no maximum. The default is 0')
parser.add_argument('--min_curvature', type=float, help='the minimum curvature of a way that should be included, 0 for no minimum. The default is 0.7 which catches most twisty roads.')
parser.add_argument('--max_curvature', type=float, help='the maximum curvature of a way that should be included, 0 for no maximum. The default is 0')
parser.add_argument('--ignored_surfaces', help='a list of the surfaces that should be ignored. The default is dirt,unpaved,gravel,sand,grass,ground')
parser.add_argument('--highway_types', help='a list of the highway types that should be included. The default is secondary,residential,tertiary,primary,primary_link,motorway,motorway_link,road,trunk,trunk_link,unclassified')
parser.add_argument('file', type=argparse.FileType('r'), help='the input file. Should be an OSM XML file.')
args = parser.parse_args()

rad_earth = 3960 # Radius of the earth in miles
settings = {
	'min_length': 2,
	'max_length': 0,
	'min_curvature': 0.7,
	'max_curvature': 0,
	'roads': ['secondary', 'residential', 'tertiary', 'primary', 'primary_link', 'motorway', 'motorway_link', 'road', 'trunk', 'trunk_link', 'unclassified'],
	'ignored_surfaces': ['dirt', 'unpaved', 'gravel', 'sand', 'grass', 'ground'],
}

# Configure settings based on the command-line arguments
if args.min_length is not None:
	settings['min_length'] = args.min_length
if args.max_length is not None:
	settings['max_length'] = args.max_length
if args.min_curvature is not None:
	settings['min_curvature'] = args.min_curvature
if args.max_curvature is not None:
	settings['max_curvature'] = args.max_curvature
if args.ignored_surfaces is not None:
	settings['ignored_surfaces'] = args.ignored_surfaces.split(',')
if args.highway_types is not None:
	settings['roads'] = args.highway_types.split(',')

# simple class that handles the parsed OSM data.
class CurvatureEvaluator(object):
	ways = []
	coords = {}
	
	def coords_callback(self, coords):
		# callback method for coords
		for osm_id, lon, lat in coords:
			self.coords[osm_id] = {'lon': lon, 'lat': lat}
			
			# status output
			if args.v:
				if not (len(self.coords) % 10000):
					sys.stdout.write('-')
					sys.stdout.flush()

	def ways_callback(self, ways):
		# callback method for ways
		for osmid, tags, refs in ways:
			if 'highway' in tags and tags['highway'] in settings['roads']:
				if 'name' not in tags or tags['name'] == '':
					continue
				if refs[0] == refs[-1]:
					continue
				if 'surface' in tags and tags['surface'] in settings['ignored_surfaces']:
					continue
				
				way = {'id': osmid, 'type': tags['highway'], 'name':tags['name'], 'refs': refs}
				if 'tiger:county' in tags:
					way['county'] = tags['tiger:county']
				else:
					way['county'] = ''
				if 'surface' in tags:
					way['surface'] = tags['surface']
				else:
					way['surface'] = 'unknown'
				self.ways = self.ways + [way]
			
			# status output
			if args.v:
				if not (len(self.ways) % 1000):
					sys.stdout.write('.')
					sys.stdout.flush()
	
	def calculate(self):
		# status output
		if args.v:
			i = 0
			total = len(self.ways)
			if total < 100:
				marker = 1
			else:
				marker = round(len(self.ways)/100)
		
		for way in self.ways:
			# status output
			if args.v:
				i = i + 1
				if not (i % marker):
					sys.stdout.write('*')
					sys.stdout.flush()
			
			start = self.coords[way['refs'][0]]
			end = self.coords[way['refs'][-1]]
			way['distance'] = distance_on_unit_sphere(start['lat'], start['lon'], end['lat'], end['lon'])
			way['length'] = 0.0
			curvature = 0.0
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
				if first_third_length > 0:
					curvature += ((first_second_length + second_third_length) / first_third_length) - 1
				
				third = second
				second = first
				second_third_length = first_second_length
			if way['length'] > 0:
				way['curvature'] = curvature
			else:
				way['curvature'] = 0
		
		# status output
		if args.v:
			print ""
				

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


# instantiate counter and parser and start parsing
evaluator = CurvatureEvaluator()
p = OSMParser(concurrency=4, ways_callback=evaluator.ways_callback, coords_callback=evaluator.coords_callback)
p.parse(args.file.name)

# status output
if args.v:
	print " "
	print "%d ways matched in %s, %d coordinates loaded." % (len(evaluator.ways), args.file.name, len(evaluator.coords))
	sys.stdout.flush()

# Loop through the ways and calculate their curvature
evaluator.calculate()

# Filter out ways that are too short/long or too straight or too curvy
if settings['min_length'] > 0:
	evaluator.ways = filter(lambda w: w['length'] * rad_earth > settings['min_length'], evaluator.ways)
if settings['max_length'] > 0:
	evaluator.ways = filter(lambda w: w['length'] * rad_earth < settings['max_length'], evaluator.ways)
if settings['min_curvature'] > 0:
	evaluator.ways = filter(lambda w: w['curvature'] > settings['min_curvature'], evaluator.ways)
if settings['max_curvature'] > 0:
	evaluator.ways = filter(lambda w: w['curvature'] < settings['max_curvature'], evaluator.ways)

# Sort the ways based on curvature
evaluator.ways = sorted(evaluator.ways, key=lambda k: k['curvature'])

# Output our tabular data
if not args.q:
	print "Curvature	Length (mi) Distance (mi)	Id				Name  			County"
	for way in evaluator.ways:
		print '%9.1f	%9.2f	%9.2f	%10s	%25s	%20s' % (way['curvature'], way['length'] * rad_earth, way['distance'] * rad_earth, way['id'], way['name'], way['county'])

if not args.no_kml:
	if args.kml_file is None:
		kml_file = args.file.name + '.kml'
	else:
		kml_file = args.kml_file.name
	# Generate KML output
	f = codecs.open(kml_file, 'w', "utf-8")
	f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')
	f.write('<Document>\n')
	f.write('	<Style id="lineStyleNormal">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>a30000ff</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	f.write('	<Style id="lineStyleHighlight">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>d30000ff</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	f.write('	<StyleMap id="lineStyle">\n')
	f.write('		<Pair>\n')
	f.write('			<key>normal</key>\n')
	f.write('			<styleUrl>#lineStyleNormal</styleUrl>\n')
	f.write('		</Pair>\n')
	f.write('		<Pair>\n')
	f.write('			<key>highlight</key>\n')
	f.write('			<styleUrl>#lineStyleHighlight</styleUrl>\n')
	f.write('		</Pair>\n')
	f.write('	</StyleMap>\n')
	evaluator.ways.reverse()
	for way in evaluator.ways:
		f.write('	<Placemark>\n')
		f.write('		<name>' + way['name'] + '</name>\n')
		f.write('		<description>' + 'Curvature: %.2f\nDistance: %.2f mi\nType: %s\nSurface: %s' % (way['curvature'], way['length'] * rad_earth, way['type'], way['surface']) + '</description>\n')
		f.write('		<styleUrl>#lineStyle</styleUrl>\n')
		f.write('		<LineString>\n')
		f.write('			<coordinates>')
		for ref in way['refs']:
			f.write("%.6f,%6f " %(evaluator.coords[ref]['lon'], evaluator.coords[ref]['lat']))
		f.write('</coordinates>\n')
		f.write('		</LineString>\n')
		f.write('	</Placemark>\n')
	
	f.write('</Document>\n')
	f.write('</kml>\n')