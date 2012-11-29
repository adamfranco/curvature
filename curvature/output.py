class Output(object):
	def __init__(self, filter):
		self.filter = filter
	
	def filter_and_sort(self, ways):
		# Filter out ways that are too short/long or too straight or too curvy
		ways = self.filter.filter(ways)
		
		# Sort the ways based on curvature
		ways = sorted(ways, key=lambda k: k['curvature'])
		
		return ways
		
class TabOutput(Output):
	def output(self, ways):
		ways = self.filter_and_sort(ways)
		
		print "Curvature	Length (mi) Distance (mi)	Id				Name  			County"
		for way in ways:
			print '%d	%9.2f	%9.2f	%10s	%25s	%20s' % (way['curvature'], way['length'] / 1609, way['distance'] / 1609, way['id'], way['name'], way['county'])

import codecs
class KmlOutput(Output):
	def _write_header(self, f):
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
	
	def _write_footer(self, f):
		f.write('</Document>\n')
		f.write('</kml>\n')
	
	def _filename_suffix(self):
		return ''
		
	def write (self, ways, path, basename):
		ways = self.filter_and_sort(ways)
		ways.reverse()
		
		filename = basename + '.c_{0:.0f}'.format(self.filter.min_curvature)
		if self.filter.max_curvature > 0:
			filename += '-{0:.0f}'.format(self.filter.max_curvature)
		if self.filter.min_length != 1 or self.filter.max_length > 0:
			filename += '.l_{0:.0f}'.format(self.filter.min_length)
		if self.filter.max_length > 0:
			filename += '-{0:.0f}'.format(self.filter.max_length)
		filename += self._filename_suffix() + '.kml'
		f = codecs.open(path + '/' + filename, 'w', "utf-8")
		
		self._write_header(f)
		self._write_ways(f, ways)
		self._write_footer(f)
		f.close()

class SingleColorKmlOutput(KmlOutput):
	
	def _write_ways(self, f, ways):
		for way in ways:
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

class MultiColorKmlOutput(KmlOutput):
	def _filename_suffix(self):
		return '.multicolor'
	
	def _write_ways(self, f, ways):
		for way in ways:
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