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
import argparse
from curvature.collector import WayCollector

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
}

# Instantiate our collector
collector = WayCollector()

# Configure settings based on the command-line arguments
collector.verbose = args.v
if args.min_length is not None:
	settings['min_length'] = args.min_length
if args.max_length is not None:
	settings['max_length'] = args.max_length
if args.min_curvature is not None:
	settings['min_curvature'] = args.min_curvature
if args.max_curvature is not None:
	settings['max_curvature'] = args.max_curvature
if args.ignored_surfaces is not None:
	collector.ignored_surfaces = args.ignored_surfaces.split(',')
if args.highway_types is not None:
	collector.roads = args.highway_types.split(',')
if args.level_1_max_radius is not None:
	collector.level_1_max_radius = args.level_1_max_radius
if args.level_1_weight is not None:
	collector.level_1_weight = args.level_1_weight
if args.level_2_max_radius is not None:
	collector.level_2_max_radius = args.level_2_max_radius
if args.level_2_weight is not None:
	collector.level_2_weight = args.level_2_weight
if args.level_3_max_radius is not None:
	collector.level_3_max_radius = args.level_3_max_radius
if args.level_3_weight is not None:
	collector.level_3_weight = args.level_3_weight
if args.level_4_max_radius is not None:
	collector.level_4_max_radius = args.level_4_max_radius
if args.level_4_weight is not None:
	collector.level_4_weight = args.level_4_weight
if args.min_lat_bound is not None:
	collector.min_lat_bound = args.min_lat_bound
if args.max_lat_bound is not None:
	collector.max_lat_bound = args.max_lat_bound
if args.min_lon_bound is not None:
	collector.min_lon_bound = args.min_lon_bound
if args.max_lon_bound is not None:
	collector.max_lon_bound = args.max_lon_bound

# start parsing
collector.load_file(args.file.name)
ways = collector.ways

# Filter out ways that are too short/long or too straight or too curvy
if settings['min_length'] > 0:
	ways = filter(lambda w: w['length'] / 1609 > settings['min_length'], ways)
if settings['max_length'] > 0:
	ways = filter(lambda w: w['length'] / 1609 < settings['max_length'], ways)
if settings['min_curvature'] > 0:
	ways = filter(lambda w: w['curvature'] > settings['min_curvature'], ways)
if settings['max_curvature'] > 0:
	ways = filter(lambda w: w['curvature'] < settings['max_curvature'], ways)

# Sort the ways based on curvature
ways = sorted(ways, key=lambda k: k['curvature'])

# Output our tabular data
if not args.q:
	print "Curvature	Length (mi) Distance (mi)	Id				Name  			County"
	for way in ways:
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
	ways.reverse()
	for way in ways:
		if args.kml_colorize:
			write_way_kml_colorize(f, way)
		else:
			write_way_kml_single_color(f, way)
	f.write('</Document>\n')
	f.write('</kml>\n')