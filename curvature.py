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

import os
import copy
import ast
import sys
import argparse
from curvature.collector import WayCollector
from curvature.filter import WayFilter
from curvature.output import TabOutput
from curvature.output import SingleColorKmlOutput
from curvature.output import MultiColorKmlOutput

parser = argparse.ArgumentParser(description='Find the roads that are most twisty in an Open Street Map (OSM) XML file.')
parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output')
parser.add_argument('-t', action='store_true', help='Display tabular output')
parser.add_argument('--no_kml', action='store_true', help='Do not generate a KML file. By default a KML file is generated with the name of the input file followed by .kml')
parser.add_argument('--output_path', type=str, help='The path under which output files should be written')
parser.add_argument('--output_basename', type=str, help='The base of the name for output files. This will be appended with a suffix and extension')
parser.add_argument('--colorize', action='store_true', help='Colorize KML lines based on the curvature of the road at each segment. Without this option roads will be lines of a single color. For large regions this may make Google Earth run slowly.')
parser.add_argument('--min_length', type=float, help='the minimum length of a way that should be included, in miles, 0 for no minimum. The default is 2.0')
parser.add_argument('--max_length', type=float, help='the maximum length of a way that should be included, in miles, 0 for no maximum. The default is 0')
parser.add_argument('--min_curvature', type=float, help='the minimum curvature of a way that should be included, 0 for no minimum. The default is 300 which catches most twisty roads.')
parser.add_argument('--max_curvature', type=float, help='the maximum curvature of a way that should be included, 0 for no maximum. The default is 0')
parser.add_argument('--add_kml', metavar='PARAMETERS', type=str, action='append', help='Output an additional KML file with alternate output parameters. PARAMETERS should be a comma-separated list of option=value that may include any of the following options: colorize, min_curvature, max_curvature, min_length, and max_length. Example: --add_kml colorize=1,min_curvature=1000')
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
parser.add_argument('file', type=argparse.FileType('r'), nargs='+', help='the input file. Should be an OSM XML file.')
args = parser.parse_args()

rad_earth_mi = 3960 # Radius of the earth in miles
rad_earth_m = 6373000 # Radius of the earth in meters

# Instantiate our collector
collector = WayCollector()
default_filter = WayFilter()

# Configure settings based on the command-line arguments
collector.verbose = args.v
if args.min_length is not None:
	default_filter.min_length = args.min_length
if args.max_length is not None:
	default_filter.max_length = args.max_length
if args.min_curvature is not None:
	default_filter.min_curvature = args.min_curvature
if args.max_curvature is not None:
	default_filter.max_curvature = args.max_curvature
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
for file in args.file:
	if args.v:
		sys.stderr.write("Loading {}\n".format(file.name))
		
	collector.load_file(file.name)
	
	
	# Output our tabular data
	if args.t:
		tab = TabOutput(default_filter)
		tab.output(collector.ways)
	
	# Generate KML output
	if not args.no_kml:
		if args.v:
			sys.stderr.write("generating KML output\n")
		
		if args.output_path is None:
			path = os.path.dirname(file.name)
		else:
			path = args.output_path
		if args.output_basename is None:
			basename = os.path.basename(file.name)
			parts = os.path.splitext(basename)
			basename = parts[0]
		else:
			basename = os.path.basename(args.output_basename)
			
		if args.colorize:
			kml = MultiColorKmlOutput(default_filter)
		else:
			kml = SingleColorKmlOutput(default_filter)
		kml.write(collector.ways, path, basename)
	
		if args.add_kml is not None:
			for opt_string in args.add_kml:
				colorize = args.colorize
				filter = copy.copy(default_filter)
				opts = opt_string.split(',')
				for opt in opts:
					opt = opt.split('=')
					key = opt[0]
					if len(opt) < 2:
						sys.stderr.write("Key '{}' passed to --add_kml has no value, ignoring.\n".format(key))
						continue
					value = opt[1]
					if key == 'colorize':
						if int(value):
							colorize = 1
						else:
							colorize = 0
					elif key == 'min_curvature':
						filter.min_curvature = float(value)
					elif key == 'max_curvature':
						filter.max_curvature = float(value)
					elif key == 'min_length':
						filter.min_length = float(value)
					elif key == 'max_length':
						filter.max_length = float(value)
					else:
						sys.stderr.write("Ignoring unknown key '{}' passed to --add_kml\n".format(key))
				
				if colorize:
					kml = MultiColorKmlOutput(filter)
				else:
					kml = SingleColorKmlOutput(filter)
				kml.write(collector.ways, path, basename)
	
if args.v:
	sys.stderr.write("done.\n")