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
		
	def write (self, ways, path, basename):
		ways = self.filter_and_sort(ways)
		ways.reverse()
		
		f = codecs.open(path + '/' + self.get_filename(basename), 'w', "utf-8")
		
		self._write_header(f)
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
	
	def get_styles(self):
		styles = {'lineStyle0':{'color':'F000E010'}} # Straight roads
		
		# Add a style for each level in a gradient from yellow to red (00FFFF - 0000FF)
		for i in range(256):
			styles['lineStyle{}'.format(i + 1)] = {'color':'F000{:02X}FF'.format(255 - i)}
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
			f.write("%.6f,%6f " %(way['segments'][0]['start'][1], way['segments'][0]['start'][0]))
			for segment in way['segments']:
				f.write("%.6f,%6f " %(segment['end'][1], segment['end'][0]))
			f.write('</coordinates>\n')
			f.write('		</LineString>\n')
			f.write('	</Placemark>\n')
	
	def level_for_curvature(self, curvature):
		if self.filter.min_curvature > 0:
			offset = self.filter.min_curvature
		else:
			offset = 0
		
		if curvature < offset:
			return 0
		
		curvature_pct = (curvature - offset) / (self.max_curvature - offset)
		# Use the square route of the ratio to give a better differentiation between
		# lower-curvature ways
		color_pct = math.sqrt(curvature_pct)
		level = int(round(255 * color_pct)) + 1		
		return level
	
	def line_style(self, way):
		return 'lineStyle{}'.format(self.level_for_curvature(way['curvature']))

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