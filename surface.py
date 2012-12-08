#!/usr/bin/env python

# surface.py
#
# Generate KML files highlighing road surface based on Open Street Map (OSM) data.
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
from curvature.collector import NoCurvatureWayCollector
from curvature.filter import WayFilter
from curvature.output import SurfaceKmlOutput

parser = argparse.ArgumentParser(description='Generate KML files highlighing road surface based on Open Street Map (OSM) data.')
parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output')
parser.add_argument('--output_path', type=str, default='.', help='The path under which output files should be written')
parser.add_argument('--output_basename', type=str, default=None, help='The base of the name for output files. This will be appended with a suffix and extension')
parser.add_argument('--min_length', type=float, default=0, help='the minimum length of a way that should be included, in miles, 0 for no minimum. The default is 0')
parser.add_argument('--max_length', type=float, default=0, help='the maximum length of a way that should be included, in miles, 0 for no maximum. The default is 0')
parser.add_argument('--add_kml', metavar='PARAMETERS', type=str, action='append', help='Output an additional KML file with alternate output parameters. PARAMETERS should be a comma-separated list of option=value that may include any of the following options: min_length, and max_length. Example: --add_kml min_length=0.5,max_length=10')
parser.add_argument('--ignored_surfaces', type=str, default='', help='a list of the surfaces that should be ignored.')
parser.add_argument('--highway_types', type=str, default='secondary,residential,tertiary,primary,primary_link,motorway,motorway_link,road,trunk,trunk_link,unclassified', help='a list of the highway types that should be included. The default is secondary,residential,tertiary,primary,primary_link,motorway,motorway_link,road,trunk,trunk_link,unclassified')
parser.add_argument('--min_lat_bound', type=float, default=None, help='The minimum latitude to include.')
parser.add_argument('--max_lat_bound', type=float, default=None, help='The maximum latitude to include.')
parser.add_argument('--min_lon_bound', type=float, default=None, help='The minimum longitude to include.')
parser.add_argument('--max_lon_bound', type=float, default=None, help='The maximum longitude to include.')
parser.add_argument('file', type=argparse.FileType('r'), nargs='+', help='the input file. Should be an OSM XML file.')
args = parser.parse_args()

rad_earth_mi = 3960 # Radius of the earth in miles
rad_earth_m = 6373000 # Radius of the earth in meters

# Instantiate our collector
collector = NoCurvatureWayCollector()
default_filter = WayFilter()

# Configure settings based on the command-line arguments
collector.verbose = args.v
default_filter.min_length = args.min_length
default_filter.max_length = args.max_length
default_filter.min_curvature = 0
default_filter.max_curvature = 0
collector.ignored_surfaces = args.ignored_surfaces.split(',')
collector.roads = args.highway_types.split(',')
collector.min_lat_bound = args.min_lat_bound
collector.max_lat_bound = args.max_lat_bound
collector.min_lon_bound = args.min_lon_bound
collector.max_lon_bound = args.max_lon_bound

# start parsing
for file in args.file:
	if args.v:
		sys.stderr.write("Loading {}\n".format(file.name))
		
	collector.load_file(file.name)
	
	# Generate KML output
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
		
	kml = SurfaceKmlOutput(default_filter)
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
				if key == 'min_length':
					filter.min_length = float(value)
				elif key == 'max_length':
					filter.max_length = float(value)
				else:
					sys.stderr.write("Ignoring unknown key '{}' passed to --add_kml\n".format(key))
			
			kml = SurfaceKmlOutput(filter)
			kml.write(collector.ways, path, basename)
	
if args.v:
	sys.stderr.write("done.\n")