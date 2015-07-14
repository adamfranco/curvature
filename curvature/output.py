import sys
import math

class Output(object):
	max_curvature = 0
	
	def __init__(self, filter):
		self.filter = filter
	
	def filter_and_sort(self, ways):
		# Filter out ways that are too short/long or too straight or too curvy
		ways = self.filter.filter(ways)
		
		# Sort the ways based on curvature
		ways = sorted(ways, key=lambda k: k['curvature'])
		
		for way in ways:
			if way['curvature'] > self.max_curvature:
				self.max_curvature = way['curvature']
		
		return ways
		
class TabOutput(Output):
	def output(self, ways):
		ways = self.filter_and_sort(ways)
		
		print "Curvature	Length (mi) Distance (mi)	Id				Name  			County"
		for way in ways:
			print '%d	%9.2f	%9.2f	%10s	%25s	%20s' % (way['curvature'], way['length'] / 1609, way['distance'] / 1609, way['id'], way['name'], way['county'])

import codecs
from xml.sax.saxutils import escape
class KmlOutput(Output):
	units = 'mi'
	
	def _write_header(self, f):
		self._write_doc_start(f)
		self._write_styles(f, self.get_styles())
	
	def _write_doc_start(self, f):
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
		f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')
		f.write('<Document>\n')
	
	def get_styles(self):
		return {
			'lineStyle0':{'color':'F000E010'}, # Straight roads
			'lineStyle1':{'color':'F000FFFF'}, # Level 1 turns
			'lineStyle2':{'color':'F000AAFF'}, # Level 2 turns
			'lineStyle3':{'color':'F00055FF'}, # Level 3 turns
			'lineStyle4':{'color':'F00000FF'}, # Level 4 turns
		}
			
		
	def _write_styles(self, f, styles):
		for id in styles:
			style = styles[id]
			if 'width' not in style:
				style['width'] = '4'
			if 'color' not in style:
				style['color'] = 'F0FFFFFF'
			
			f.write('	<Style id="' + id + '">\n')
			f.write('		<LineStyle>\n')
			f.write('			<color>' + style['color'] + '</color>\n')
			f.write('			<width>' + style['width'] + '</width>\n')
			f.write('		</LineStyle>\n')
			f.write('	</Style>\n')		
	
	def _write_footer(self, f):
		f.write('</Document>\n')
		f.write('</kml>\n')
	
	def _filename_suffix(self):
		return ''
	
	def _write_region(self, f, ways):
		min_lat = ways[0]['segments'][0]['start'][0]
		max_lat = ways[0]['segments'][0]['start'][0]
		min_lon = ways[0]['segments'][0]['start'][1]
		max_lon = ways[0]['segments'][0]['start'][1]
		for way in ways:
			way_max_lat = self.get_way_max_lat(way)
			if way_max_lat > max_lat:
				max_lat = way_max_lat
			way_min_lat = self.get_way_min_lat(way)
			if way_min_lat < min_lat:
				min_lat = way_min_lat
			way_max_lon = self.get_way_max_lon(way)
			if way_max_lon > max_lon:
				max_lon = way_max_lon
			way_min_lon = self.get_way_min_lon(way)
			if way_min_lon < min_lon:
				min_lon = way_min_lon
		
# 		f.write('	<!--\n')
# 		f.write('	<Region>\n')
		f.write('		<LatLonBox>\n')
		f.write('			<north>%.6f</north>\n' % (max_lat))
		f.write('			<south>%.6f</south>\n' % (min_lat))
		# Note that this won't work for regions crossing longitude 180, but this
		# should only affect the Russian asian file
		f.write('			<east>%.6f</east>\n' % (max_lon))
		f.write('			<west>%.6f</west>\n' % (min_lon))
		f.write('		</LatLonBox>\n')
# 		f.write('	</Region>\n')
# 		f.write('	-->\n')
	
	def get_way_max_lat(self, way):
		if 'max_lat' not in way:
			self.store_way_region(way)
		return way['max_lat']
	
	def get_way_min_lat(self, way):
		if 'min_lat' not in way:
			self.store_way_region(way)
		return way['min_lat']
	
	def get_way_max_lon(self, way):
		if 'max_lon' not in way:
			self.store_way_region(way)
		return way['max_lon']
		
	def get_way_min_lon(self, way):
		if 'min_lon' not in way:
			self.store_way_region(way)
		return way['min_lon']
	
	def store_way_region(self, way):
		way['max_lat'] = way['segments'][0]['start'][0]
		way['min_lat'] = way['segments'][0]['start'][0]
		way['max_lon'] = way['segments'][0]['start'][1]
		way['min_lon'] = way['segments'][0]['start'][1]
		for segment in way['segments']:
			if segment['end'][0] > way['max_lat']:
				way['max_lat'] = segment['end'][0]
			if segment['end'][0] < way['min_lat']:
				way['min_lat'] = segment['end'][0]
			if segment['end'][1] > way['max_lon']:
				way['max_lon'] = segment['end'][1]
			if segment['end'][1] < way['min_lon']:
				way['min_lon'] = segment['end'][1]
	
	def write (self, ways, path, basename):
		ways = self.filter_and_sort(ways)
		ways.reverse()
		
		f = codecs.open(path + '/' + self.get_filename(basename), 'w', "utf-8")
		
		self._write_header(f)
		self._write_region(f, ways)
		self._write_ways(f, ways)
		self._write_footer(f)
		f.close()
	
	def get_filename(self, basename):
		filename = basename + '.c_{0:.0f}'.format(self.filter.min_curvature)
		if self.filter.max_curvature > 0:
			filename += '-{0:.0f}'.format(self.filter.max_curvature)
		if self.filter.min_length != 1 or self.filter.max_length > 0:
			filename += '.l_{0:.0f}'.format(self.filter.min_length)
		if self.filter.max_length > 0:
			filename += '-{0:.0f}'.format(self.filter.max_length)
		filename += self._filename_suffix() + '.kml'
		return filename;
	
	def get_description(self, way):
		if self.units == 'km':
			return 'Curvature: %.2f\nDistance: %.2f km\nType: %s\nSurface: %s' % (way['curvature'], way['length'] / 1000, way['type'], way['surface']) 
		else:
			return 'Curvature: %.2f\nDistance: %.2f mi\nType: %s\nSurface: %s' % (way['curvature'], way['length'] / 1609, way['type'], way['surface']) 

class SingleColorKmlOutput(KmlOutput):
	
	relative_color = False
	
	def __init__(self, filter, relative_color):
		super(SingleColorKmlOutput, self).__init__(filter)
		self.relative_color = relative_color
	
	def get_styles(self):
		styles = {'lineStyle0':{'color':'F000E010'}} # Straight roads
		
		# Add a style for each level in a gradient from yellow to red (00FFFF - 0000FF)
		for i in range(256):
			styles['lineStyle{}'.format(i + 1)] = {'color':'F000{:02X}FF'.format(255 - i)}
		
		# Add a style for each level in a gradient from red to magenta (0000FF - FF00FF)
		for i in range(1, 256):
			styles['lineStyle{}'.format(i + 256)] = {'color':'F0{:02X}00FF'.format(i)}
	
		return styles
	
	def _write_ways(self, f, ways):
		
		for way in ways:
			if 'segments' not in way or not len(way['segments']):
# 				sys.stderr.write("\nError: way has no segments: {} \n".format(way['name']))
				continue
			f.write('	<Placemark>\n')
			f.write('		<styleUrl>#' + self.line_style(way) + '</styleUrl>\n')
			f.write('		<name>' + escape(way['name']) + '</name>\n')
			f.write('		<description>' + self.get_description(way) + '</description>\n')
			f.write('		<LineString>\n')
			f.write('			<tessellate>1</tessellate>\n')
			f.write('			<coordinates>')
			self._write_segments(f, way['segments']);
			f.write('</coordinates>\n')
			f.write('		</LineString>\n')
			f.write('	</Placemark>\n')
	
	def _write_segments(self, f, segments):
		f.write("%.6f,%6f " %(segments[0]['start'][1], segments[0]['start'][0]))
		for segment in segments:
			f.write("%.6f,%6f " %(segment['end'][1], segment['end'][0]))
	
	
	def level_for_curvature(self, curvature):
		if self.relative_color:
			return self.relative_level_for_curvature(curvature)
		else:
			return self.absolute_level_for_curvature(curvature)
	
	def relative_level_for_curvature(self, curvature):
		if self.filter.min_curvature > 0:
			offset = self.filter.min_curvature
		else:
			offset = 0
		
		if curvature < offset:
			return 0
		
		curvature_pct = (curvature - offset) / (self.max_curvature - offset)
		
		# Map ratio to a logarithmic scale to give a better differentiation 
		# between lower-curvature ways. 10,000 is max red.
		# y = 1-1/(10^(x*2))
		color_pct = 1 - 1/math.pow(10, curvature_pct * 2)
		
		level = int(round(510 * color_pct)) + 1		
		return level
	
	def absolute_level_for_curvature(self, curvature):
		if self.filter.min_curvature > 0:
			offset = self.filter.min_curvature
		else:
			offset = 0
		
		if curvature < offset:
			return 0
		
		# Define a global max rather than just the maximum found in the input.
		# This will cause the color levels to be the same across inputs for the same
		# filter minimum.
		max = 40000
		
		curvature_pct = min((curvature - offset) / (max - offset), 1)
		
		# Map ratio to a logarithmic scale to give a better differentiation 
		# between lower-curvature ways. 10,000 is max red.
		# y = 1-1/(10^(x*2))
		color_pct = 1 - 1/math.pow(10, curvature_pct * 2)
		
		level = int(round(510 * color_pct)) + 1

# 		sys.stderr.write("Curvature: {}, curvature_pct: {}, color_pct: {}, level: {}.\n".format(curvature, curvature_pct, color_pct, level))
		
		return level
	
	def line_style(self, way):
		return 'lineStyle{}'.format(self.level_for_curvature(way['curvature']))

class ReducedPointsSingleColorKmlOutput(SingleColorKmlOutput):
	num_points = 2
	
	def __init__(self, filter, relative_color, num_points):
		super(ReducedPointsSingleColorKmlOutput, self).__init__(filter, relative_color)
		num_points = int(num_points)
		if num_points > self.num_points:
			self.num_points = num_points
	
	def _write_segments(self, f, segments):
		num_segments = len(segments)
		interval = math.ceil((num_segments) / (self.num_points - 1))
		
		# write the first point
		f.write("%.6f,%6f " %(segments[0]['start'][1], segments[0]['start'][0]))
		
		i = 0
		j = 0
		for segment in segments:
			i = i + 1
			j = j + 1
			
			# Print the last of the interval, plus the last
			if j == interval or i == num_segments:
				f.write("%.6f,%6f " %(segment['end'][1], segment['end'][0]))
				j = 0

class MultiColorKmlOutput(KmlOutput):
	def _filename_suffix(self):
		return '.multicolor'
	
	def _write_ways(self, f, ways):
		f.write('	<Style id="folderStyle">\n')
		f.write('		<ListStyle>\n')
		f.write('			<listItemType>checkHideChildren</listItemType>\n')
		f.write('		</ListStyle>\n')
		f.write('	</Style>\n')
		
		for way in ways:
			f.write('	<Folder>\n')
			f.write('		<styleUrl>#folderStyle</styleUrl>\n')
			f.write('		<name>' + escape(way['name']) + '</name>\n')
			f.write('		<description>' + self.get_description(way) + '</description>\n')
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
					f.write("%.6f,%6f " %(segment['start'][1], segment['start'][0]))
				f.write("%.6f,%6f " %(segment['end'][1], segment['end'][0]))
				i = i + 1
			if i:
				f.write('</coordinates>\n')
				f.write('			</LineString>\n')
				f.write('		</Placemark>\n')
			f.write('	</Folder>\n')

class SurfaceKmlOutput(SingleColorKmlOutput):
	def __init__(self, filter):
		super(SurfaceKmlOutput, self).__init__(filter, False)

	def get_styles(self):
		return {
			'unknown':{'color':'F0FFFFFF'},
			'paved':{'color':'F0000000'},
			'asphalt':{'color':'F0FF0000'},
			'concrete':{'color':'F0FF4444'},
			'concrete:lanes':{'color':'F0FFCCCC'},
			'concrete:plates':{'color':'F0FFCCCC'},
			'cobblestone':{'color':'F0FF8888'},
			'cobblestone:flattened':{'color':'F0FF8888'},
			'paving_stones':{'color':'F0FF8888'},
			'paving_stones:20':{'color':'F0FF8888'},
			'paving_stones:30':{'color':'F0FF8888'},
			
			'unpaved':{'color':'F000FFFF'},
			'fine_gravel':{'color':'F00055FF'},
			'pebblestone':{'color':'F000AAFF'},
			'gravel':{'color':'F000AAFF'},
			'dirt':{'color':'F06780E5'},#E58067
			'sand':{'color':'F000AAAA'},
			'salt':{'color':'F000AAAA'},
			'ice':{'color':'F000AAAA'},
			'grass':{'color':'F000FF00'},
			'ground':{'color':'F000FF00'},
			'earth':{'color':'F000FF00'},
			'mud':{'color':'F00000FF'},

		}
	
	def line_style(self, way):
		return way['surface']
	
	def get_filename(self, basename):
		filename = basename + '.surfaces'
		if self.filter.min_length > 0 or self.filter.max_length > 0:
			filename += '.l_{0:.0f}'.format(self.filter.min_length)
		if self.filter.max_length > 0:
			filename += '-{0:.0f}'.format(self.filter.max_length)
		filename += self._filename_suffix() + '.kml'
		return filename;
		
	def get_description(self, way):
		return 'Type: %s\nSurface: %s' % (way['type'], way['surface'])