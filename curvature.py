#!/usr/bin/env python

# curvature.py
#
# Find roads that are the most curved or twisty based on Open Street Map (OSM) data.
#
# The goal of this script is to help those who enjoy twisty roads (such as 
# motorcycle or driving enthusiasts) to find promising roads that are not well known.
# It works by calculating a synthetic "curvature" parameter for each road segment
# (known as a "way" in OSM parlance) that represents how twisty that segment is. 
# These twisty segments can then be output as KML files that can be viewed in Google Earth
# or viewed in tabular form.
# 
# About the "curvature" parameter:
# The "curvature" of a way is determined by iterating over every set of three points
# in the line. Each set of three points form a triangle and that triangle has a circumcircle
# whose radius corresponds to the radius of the curve for that set. Since every line
# segment (between two points) is part of two separate triangles, the radius of the curve
# at that segment is considdered to be the average of the radii for its member sets.
# Now that we have a curve radius for each segment we can categorize each segment into
# ranges of radii from very tight (short radius turn) to very broad or straight (long radius turn).
# Once each segment is categorized its length can be multiplied by a weighting (by default
# zero for straight segments, 1 for broad curves, and up to 2 for the tightest curves).
# The sum of all of these weighting gives us a number for curvature that corresponds
# proportionally to the distance (in meters) that you will be in a turn.*
# 
# * If all weights are 1 then the curvature parameter will be exactly the distance
#   in turns. The goal of this project however is to prefer tighter turns, so sharp
#   corners are given an increased weight.
# 
# Author: Adam Franco
# https://github.com/adamfranco/curvature
# Copyright 2012 Adam Franco
# License: GNU General Public License Version 3 or later

import codecs
import sys
import math
from imposm.parser import OSMParser
import argparse

parser = argparse.ArgumentParser(description='Find the roads that are most twisty in an Open Street Map (OSM) XML file.')
parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output')
parser.add_argument('-q', action='store_true', help='Quiet mode, do not output tabular data')
parser.add_argument('--no_kml', action='store_true', help='Do not generate a KML file. By default a KML file is generated with the name of the input file followed by .kml')
parser.add_argument('--kml_file', type=argparse.FileType('w'), help='A custom destination for the KML file')
parser.add_argument('--kml_colorize', action='store_true', help='Colorize KML lines based on the curvature of the road at each segment. Without this option roads will be lines of a single color. For large regions this may make Google Earth run slowly.')
parser.add_argument('--min_length', type=float, help='the minimum length of a way that should be included, in miles, 0 for no minimum. The default is 2.0')
parser.add_argument('--max_length', type=float, help='the maximum length of a way that should be included, in miles, 0 for no maximum. The default is 0')
parser.add_argument('--min_curvature', type=float, help='the minimum curvature of a way that should be included, 0 for no minimum. The default is 300 which catches most twisty roads.')
parser.add_argument('--max_curvature', type=float, help='the maximum curvature of a way that should be included, 0 for no maximum. The default is 0')
parser.add_argument('--level_1_max_radius', type=int, help='the maximum radius of a curve (in meters) that will be considered part of level 1. Curves with radii larger than this will be considered straight. The default is 175')
parser.add_argument('--level_1_weight', type=float, help='the weight to give segments that are classified as level 1. Default 1')
parser.add_argument('--level_2_max_radius', type=int, help='the maximum radius of a curve (in meters) that will be considered part of level 2. The default is 100')
parser.add_argument('--level_2_weight', type=float, help='the weight to give segments that are classified as level 2. Default 1.3')
parser.add_argument('--level_3_max_radius', type=int, help='the maximum radius of a curve (in meters) that will be considered part of level 3. The default is 60')
parser.add_argument('--level_3_weight', type=float, help='the weight to give segments that are classified as level 3. Default 1.6')
parser.add_argument('--level_4_max_radius', type=int, help='the maximum radius of a curve (in meters) that will be considered part of level 4. The default is 30')
parser.add_argument('--level_4_weight', type=float, help='the weight to give segments that are classified as level 4. Default 2')
parser.add_argument('--ignored_surfaces', help='a list of the surfaces that should be ignored. The default is dirt,unpaved,gravel,sand,grass,ground')
parser.add_argument('--highway_types', help='a list of the highway types that should be included. The default is secondary,residential,tertiary,primary,primary_link,motorway,motorway_link,road,trunk,trunk_link,unclassified')
parser.add_argument('--min_lat_bound', type=float, help='The minimum latitude to include.')
parser.add_argument('--max_lat_bound', type=float, help='The maximum latitude to include.')
parser.add_argument('--min_lon_bound', type=float, help='The minimum longitude to include.')
parser.add_argument('--max_lon_bound', type=float, help='The maximum longitude to include.')
parser.add_argument('file', type=argparse.FileType('r'), help='the input file. Should be an OSM XML file.')
args = parser.parse_args()

rad_earth_mi = 3960 # Radius of the earth in miles
rad_earth_m = 6373000 # Radius of the earth in meters
settings = {
	'min_length': 1,
	'max_length': 0,
	'min_curvature': 300,
	'max_curvature': 0,
	'roads': ['secondary', 'residential', 'tertiary', 'primary', 'primary_link', 'motorway', 'motorway_link', 'road', 'trunk', 'trunk_link', 'unclassified'],
	'ignored_surfaces': ['dirt', 'unpaved', 'gravel', 'sand', 'grass', 'ground'],
	'level_1_max_radius': 175,
	'level_1_weight': 1,
	'level_2_max_radius': 100,
	'level_2_weight': 1.3,
	'level_3_max_radius': 60,
	'level_3_weight': 1.6,
	'level_4_max_radius': 30,
	'level_4_weight': 2,
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
if args.level_1_max_radius is not None:
	settings['level_1_max_radius'] = args.level_1_max_radius
if args.level_1_weight is not None:
	settings['level_1_weight'] = args.level_1_weight
if args.level_2_max_radius is not None:
	settings['level_2_max_radius'] = args.level_2_max_radius
if args.level_2_weight is not None:
	settings['level_2_weight'] = args.level_2_weight
if args.level_3_max_radius is not None:
	settings['level_3_max_radius'] = args.level_3_max_radius
if args.level_3_weight is not None:
	settings['level_3_weight'] = args.level_3_weight
if args.level_4_max_radius is not None:
	settings['level_4_max_radius'] = args.level_4_max_radius
if args.level_4_weight is not None:
	settings['level_4_weight'] = args.level_4_weight


# simple class that handles the parsed OSM data.
class CurvatureEvaluator(object):
	ways = []
	coords = {}
	num_coords = 0
	num_ways = 0
	
	def coords_callback(self, coords):
		# callback method for coords
		for osm_id, lon, lat in coords:
			if args.min_lat_bound and lat < args.min_lat_bound:
				continue
			if args.max_lat_bound and lat > args.max_lat_bound:
				continue
			if args.min_lon_bound and lon < args.min_lon_bound:
				continue
			if args.max_lon_bound and lon > args.max_lon_bound:
				continue
			
			self.coords[osm_id] = {'lon': lon, 'lat': lat}
			
			# status output
			if args.v:
				self.num_coords = self.num_coords + 1
				if not (self.num_coords % 10000):
					sys.stdout.write('.')
					sys.stdout.flush()

	def ways_callback(self, ways):
		# callback method for ways
		for osmid, tags, refs in ways:
			if refs[0] == refs[-1]:
				continue
			
			if args.min_lat_bound or args.max_lat_bound or args.min_lon_bound or args.min_lat_bound:
				try:
					start = self.coords[refs[0]]
					if args.min_lat_bound and start['lat'] < args.min_lat_bound:
						continue
					if args.max_lat_bound and start['lat'] > args.max_lat_bound:
						continue
					if args.min_lon_bound and start['lon'] < args.min_lon_bound:
						continue
					if args.max_lon_bound and start['lon'] > args.max_lon_bound:
						continue
				except:
					continue
			
			if 'name' not in tags or tags['name'] == '':
				continue
			if 'surface' in tags and tags['surface'] in settings['ignored_surfaces']:
				continue
			if 'highway' in tags and tags['highway'] in settings['roads']:
				way = {'id': osmid, 'type': tags['highway'], 'name':tags['name'], 'refs': refs}
				if 'tiger:county' in tags:
					way['county'] = tags['tiger:county']
				else:
					way['county'] = ''
				if 'surface' in tags:
					way['surface'] = tags['surface']
				else:
					way['surface'] = 'unknown'
				
				try:
					self.calculate_distance_and_curvature(way)
				except:
					continue
				
				self.ways.append(way)
			
			# status output
			if args.v:
				self.num_ways = self.num_ways + 1
				if not (self.num_ways % 1000):
					sys.stdout.write('-')
					sys.stdout.flush()
	
	def calculate_distance_and_curvature(self, way):
		way['distance'] = 0.0
		way['curvature'] = 0.0
		way['length'] = 0.0
		start = self.coords[way['refs'][0]]
		end = self.coords[way['refs'][-1]]
		way['distance'] = distance_on_unit_sphere(start['lat'], start['lon'], end['lat'], end['lon']) * rad_earth_m
		second = 0
		third = 0
		segments = []
		for ref in way['refs']:
			first = self.coords[ref]
			
			if not second:
				second = first
				continue
			
			first_second_length = distance_on_unit_sphere(first['lat'], first['lon'], second['lat'], second['lon']) * rad_earth_m
			way['length'] += first_second_length
			
			if not third:
				third = second
				second = first
				second_third_length = first_second_length
				continue
			
			first_third_length = distance_on_unit_sphere(first['lat'], first['lon'], third['lat'], third['lon']) * rad_earth_m
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
				# set the radius of the previous segment to the average radius of both circumcircles it's a part of
				segments[-1]['radius'] = (segments[-1]['radius'] + r) / 2
			# Add our latest segment
			segments.append({'start': second, 'end': first, 'length': first_second_length, 'radius': r})
			
			third = second
			second = first
			second_third_length = first_second_length
		
		way['segments'] = segments

		# Calculate the curvature as a weighted distance traveled at each curvature.
		way['curvature'] = 0
		for segment in segments:
			if segment['radius'] < settings['level_4_max_radius']:
				segment['curvature_level'] = 4
				way['curvature'] += segment['length'] * settings['level_4_weight']
			elif segment['radius'] < settings['level_3_max_radius']:
				segment['curvature_level'] = 3
				way['curvature'] += segment['length'] * settings['level_3_weight']
			elif segment['radius'] < settings['level_2_max_radius']:
				segment['curvature_level'] = 2
				way['curvature'] += segment['length'] * settings['level_2_weight']
			elif segment['radius'] < settings['level_1_max_radius']:
				segment['curvature_level'] = 1
				way['curvature'] += segment['length'] * settings['level_1_weight']
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


# instantiate counter and parser and start parsing
evaluator = CurvatureEvaluator()
p = OSMParser(ways_callback=evaluator.ways_callback, coords_callback=evaluator.coords_callback)
p.parse(args.file.name)

# status output
if args.v:
	print " "
	print "%d ways matched in %s, %d coordinates loaded." % (len(evaluator.ways), args.file.name, len(evaluator.coords))
	sys.stdout.flush()

# Filter out ways that are too short/long or too straight or too curvy
if settings['min_length'] > 0:
	evaluator.ways = filter(lambda w: w['length'] / 1609 > settings['min_length'], evaluator.ways)
if settings['max_length'] > 0:
	evaluator.ways = filter(lambda w: w['length'] / 1609 < settings['max_length'], evaluator.ways)
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
		print '%d	%9.2f	%9.2f	%10s	%25s	%20s' % (way['curvature'], way['length'] / 1609, way['distance'] / 1609, way['id'], way['name'], way['county'])

def write_way_kml_colorize(f, way):
	f.write('	<Folder>\n')
	f.write('		<styleUrl>#folderStyle</styleUrl>\n')
	f.write('		<name>' + way['name'] + '</name>\n')
	f.write('		<description>' + 'Curvature: %.2f\nDistance: %.2f mi\nType: %s\nSurface: %s' % (way['curvature'], way['length'] / 1609, way['type'], way['surface']) + '</description>\n')
	current_curvature_level = 0
	i = 0
	for segment in way['segments']:
		if segment['curvature_level'] != current_curvature_level or not i:
			current_curvature_level = segment['curvature_level']
			# Close the open LineString
			if i:
				f.write('</coordinates>\n')
				f.write('			</LineString>\n')
				f.write('		</Placemark>\n')
			# Start a new linestring for this level
			f.write('		<Placemark>\n')
			f.write('			<styleUrl>#lineStyle%d</styleUrl>\n' % (current_curvature_level))
			f.write('			<LineString>\n')
			f.write('				<tessellate>1</tessellate>\n')
			f.write('				<coordinates>')
			f.write("%.6f,%6f " %(segment['start']['lon'], segment['start']['lat']))
		f.write("%.6f,%6f " %(segment['end']['lon'], segment['end']['lat']))
		i = i + 1
	if i:
		f.write('</coordinates>\n')
		f.write('			</LineString>\n')
		f.write('		</Placemark>\n')
	f.write('	</Folder>\n')
	
def write_way_kml_single_color(f, way):
	f.write('	<Placemark>\n')
	f.write('		<styleUrl>#lineStyle4</styleUrl>\n')
	f.write('		<name>' + way['name'] + '</name>\n')
	f.write('		<description>' + 'Curvature: %.2f\nDistance: %.2f mi\nType: %s\nSurface: %s' % (way['curvature'], way['length'] / 1609, way['type'], way['surface']) + '</description>\n')
	f.write('		<LineString>\n')
	f.write('			<tessellate>1</tessellate>\n')
	f.write('			<coordinates>')
	f.write("%.6f,%6f " %(way['segments'][0]['start']['lon'], way['segments'][0]['start']['lat']))
	for segment in way['segments']:
		f.write("%.6f,%6f " %(segment['end']['lon'], segment['end']['lat']))

	f.write('</coordinates>\n')
	f.write('		</LineString>\n')
	f.write('	</Placemark>\n')

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
	# Straight roads
	f.write('	<Style id="lineStyle0">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>F000E010</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	# Level 1 turns
	f.write('	<Style id="lineStyle1">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>F000FFFF</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	# Level 2 turns
	f.write('	<Style id="lineStyle2">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>F000AAFF</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	# Level 3 turns
	f.write('	<Style id="lineStyle3">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>F00055FF</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	# Level 4 turns
	f.write('	<Style id="lineStyle4">\n')
	f.write('		<LineStyle>\n')
	f.write('			<color>F00000FF</color>\n')
	f.write('			<width>4</width>\n')
	f.write('		</LineStyle>\n')
	f.write('	</Style>\n')
	f.write('	<Style id="folderStyle">\n')
	f.write('		<ListStyle>\n')
	f.write('			<listItemType>checkHideChildren</listItemType>\n')
	f.write('		</ListStyle>\n')
	f.write('	</Style>\n')
	evaluator.ways.reverse()
	for way in evaluator.ways:
		if args.kml_colorize:
			write_way_kml_colorize(f, way)
		else:
			write_way_kml_single_color(f, way)
	f.write('</Document>\n')
	f.write('</kml>\n')