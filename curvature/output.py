import sys
import math
import string
from collections import Counter
import os
import codecs
from xml.sax.saxutils import escape

class KmlOutput(object):
	units = 'mi'
	no_compress = False

	def __init__(self, units):
		if units in ['mi', 'km']:
			self.units = units
		else:
			raise ValueError("units must be 'mi' or 'km'")

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
			'elminiated':{'color':'F0000000'}, # Eliminated segments
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

	def _record_bbox(self, way):
		if not hasattr(self, 'min_lat') and 'segments' in way and len(way['segments']):
			self.min_lat = way['segments'][0]['start'][0]
			self.max_lat = way['segments'][0]['start'][0]
			self.min_lon = way['segments'][0]['start'][1]
			self.max_lon = way['segments'][0]['start'][1]
		way_max_lat = self.get_way_max_lat(way)
		if way_max_lat > self.max_lat:
			self.max_lat = way_max_lat
		way_min_lat = self.get_way_min_lat(way)
		if way_min_lat < self.min_lat:
			self.min_lat = way_min_lat
		way_max_lon = self.get_way_max_lon(way)
		if way_max_lon > self.max_lon:
			self.max_lon = way_max_lon
		way_min_lon = self.get_way_min_lon(way)
		if way_min_lon < self.min_lon:
			self.min_lon = way_min_lon

	def _write_region(self, f):
		if not hasattr(self, 'max_lat'):
			return

# 		f.write('	<!--\n')
# 		f.write('	<Region>\n')
		f.write('		<LatLonBox>\n')
		f.write('			<north>%.6f</north>\n' % (self.max_lat))
		f.write('			<south>%.6f</south>\n' % (self.min_lat))
		# Note that this won't work for regions crossing longitude 180, but this
		# should only affect the Russian asian file
		f.write('			<east>%.6f</east>\n' % (self.max_lon))
		f.write('			<west>%.6f</west>\n' % (self.min_lon))
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

	def head (self, f):
		self._write_header(f)

	def write_way(self, f, way):
		self._record_bbox(way)
		self._write_way(f, way)

	def foot (self, f):
		self._write_region(f)
		self._write_footer(f)

	def get_description(self, way):
		if self.units == 'km':
			description = 'Curvature: %.2f\nDistance: %.2f km\n' % (way['curvature'], way['length'] / 1000)
		else:
			description = 'Curvature: %.2f\nDistance: %.2f mi\n' % (way['curvature'], way['length'] / 1609)

		description = description + 'Type: %s\nSurface: %s\n' % (way['type'], self.get_surfaces(way))
		description = description + '\nConstituent ways - <em>Open/edit in OpenStreetMap:</em>\n%s\n\n%s\n' % (self.get_constituent_list(way), self.get_all_josm_link(way))
		return '<div style="width: 500px">%s</div>' % (string.replace(description, '\n', '<br/>'))

	def get_surfaces(self, way):
		if 'constituents' in way:
			surfaces = []
			for constituent in way['constituents']:
				surfaces.append(constituent['surface'])
			surface_list = [surface[0] for surface in Counter(surfaces).most_common()]
			return ', '.join(surface_list)
		else:
			return way['surface']

	def get_all_josm_link(self, way):
		select = []
		for c in way['constituents']:
			select.append('way%d' % c['id'])
		josm_url ='http://127.0.0.1:8111/load_and_zoom?left=%.5f&right=%.5f&top=%.5f&bottom=%.5f&select=%s' % (self.get_way_min_lon(way) - 0.001, self.get_way_max_lon(way) + 0.001, self.get_way_max_lat(way) + 0.001, self.get_way_min_lat(way) - 0.001, ','.join(select))
		josm_link = '<a href="" onclick="var img=document.createElement(\'img\'); img.style.display=\'none\'; img.src=\'%s\'; this.parentElement.appendChild(img); return false;">Edit all in JOSM</a>' % (josm_url)
		coords_lat = ((self.get_way_max_lat(way) - self.get_way_min_lat(way))/2) + self.get_way_min_lat(way)
		coords_lon = ((self.get_way_max_lon(way) - self.get_way_min_lon(way))/2) + self.get_way_min_lon(way)
		coords = '<a href="" onclick="if (this.nextSibling.style.display==\'inline\') {this.nextSibling.style.display=\'none\';} else { this.nextSibling.style.display=\'inline\'; this.nextSibling.select() } return false;">coords </a><input type="text" style="display: none;" value="%.5f,%.5f"/>' % (coords_lon, coords_lat)
		return josm_link + ', ' + coords

	def get_constituent_list(self, way):
		list = '<table style="width: 100%; text-align: center;">'
		list += '<tr><th>View</th><th>Surface</th><th>Actions</th></tr>'
		for c in way['constituents']:
			view_link = '<a href="https://www.openstreetmap.org/way/%d">%d</a>' % (c['id'], c['id'])
			josm_url = 'http://127.0.0.1:8111/load_and_zoom?left=%.5f&right=%.5f&top=%.5f&bottom=%.5f&select=way%d' % (self.get_way_min_lon(c) - 0.001, self.get_way_max_lon(c) + 0.001, self.get_way_max_lat(c) + 0.001, self.get_way_min_lat(c) - 0.001, c['id'])
			josm_link = '<a href="" onclick="var img=document.createElement(\'img\'); img.style.display=\'none\'; img.src=\'%s\'; this.parentElement.appendChild(img); return false;">Edit in JOSM</a>' % (josm_url)
			coords_lat = ((self.get_way_max_lat(c) - self.get_way_min_lat(c))/2) + self.get_way_min_lat(c)
			coords_lon = ((self.get_way_max_lon(c) - self.get_way_min_lon(c))/2) + self.get_way_min_lon(c)
			web_edit_url = 'https://www.openstreetmap.org/edit?way=%d#map=16/%.4f/%.4f' % (c['id'], coords_lat, coords_lon)
			web_edit_link = '<a href="%s">Web Edit</a>' % (web_edit_url)
			coords = '<a href="" onclick="if (this.nextSibling.style.display==\'block\') {this.nextSibling.style.display=\'none\';} else { this.nextSibling.style.display=\'block\'; this.nextSibling.select() } return false;">coords</a><input type="text" style="display: none;" value="%.5f,%.5f"/>' % (coords_lon, coords_lat)
			list += '<tr><td>%s</td><td>%s</td><td>%s, %s, %s</td></tr>' % (view_link, c['surface'], web_edit_link, josm_link, coords)

		list += '</table>'
		return list

class SingleColorKmlOutput(KmlOutput):

	min_curvature = 0
	max_curvature = 4000

	def __init__(self, units, min_curvature, max_curvature):
		super(SingleColorKmlOutput, self).__init__(units)
		self.min_curvature = min_curvature
		self.max_curvature = max_curvature

	def get_styles(self):
		styles = {'lineStyle0':{'color':'F000E010'}} # Straight roads

		# Add a style for each level in a gradient from yellow to red (00FFFF - 0000FF)
		for i in range(256):
			styles['lineStyle{}'.format(i + 1)] = {'color':'F000{:02X}FF'.format(255 - i)}

		# Add a style for each level in a gradient from red to magenta (0000FF - FF00FF)
		for i in range(1, 256):
			styles['lineStyle{}'.format(i + 256)] = {'color':'F0{:02X}00FF'.format(i)}

		return styles

	def _write_way(self, f, way):
		if 'segments' not in way or not len(way['segments']):
# 				sys.stderr.write("\nError: way has no segments: {} \n".format(way['name']))
			return
		f.write('	<Placemark>\n')
		f.write('		<styleUrl>#' + self.line_style(way) + '</styleUrl>\n')
		f.write('		<name>' + escape(way['name']) + '</name>\n')
		f.write('		<description><![CDATA[' + self.get_description(way) + ']]></description>\n')
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
		offset = self.min_curvature

		if curvature < offset:
			return 0

		# Define a global max rather than just the maximum found in the input.
		# This will cause the color levels to be the same across inputs for the same
		# filter minimum.
		max = self.max_curvature

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


class MultiColorKmlOutput(KmlOutput):

	def head(self, f):
		super(MultiColorKmlOutput, self).head(f)
		f.write('	<Style id="folderStyle">\n')
		f.write('		<ListStyle>\n')
		f.write('			<listItemType>checkHideChildren</listItemType>\n')
		f.write('		</ListStyle>\n')
		f.write('	</Style>\n')

	def _write_way(self, f, way):
		f.write('	<Folder>\n')
		f.write('		<styleUrl>#folderStyle</styleUrl>\n')
		f.write('		<name>' + escape(way['name']) + '</name>\n')
		f.write('		<description><![CDATA[' + self.get_description(way) + ']]></description>\n')
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
				if 'eliminated' in segment:
					f.write('			<styleUrl>#elminiated</styleUrl>\n')
				else:
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

	def __init__(self, units):
		super(SurfaceKmlOutput, self).__init__(units, 0, 4000)

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

	def get_description(self, way):
		return 'Type: %s\nSurface: %s' % (way['type'], way['surface'])
