# -*- coding: UTF-8 -*-
import sys
import math
import string
from collections import Counter
import os
from xml.sax.saxutils import escape

class OutputTools(object):
    units = 'mi'
    assumed_paved_highways = ('motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link')
    paved_surfaces = ('paved', 'asphalt', 'concrete', 'concrete:lanes', 'concrete:plates', 'metal', 'wood', 'cobblestone')

    def __init__(self, units, assumed_paved_highways=None, paved_surfaces=None):
        if units in ['mi', 'km']:
            self.units = units
        else:
            raise ValueError("units must be 'mi' or 'km'")
        if assumed_paved_highways is not None:
            self.assumed_paved_highways = assumed_paved_highways
        if paved_surfaces is not None:
            self.paved_surfaces = paved_surfaces


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

    def get_collection_max_lat(self, collection):
        max = self.get_way_max_lat(collection['ways'][0])
        for i in range(1, len(collection['ways'])):
            way_max = self.get_way_max_lat(collection['ways'][i])
            if way_max > max:
                max = way_max
        return max

    def get_collection_min_lat(self, collection):
        min = self.get_way_min_lat(collection['ways'][0])
        for i in range(1, len(collection['ways'])):
            way_min = self.get_way_min_lat(collection['ways'][i])
            if way_min < min:
                min = way_min
        return min

    def get_collection_max_lon(self, collection):
        max = self.get_way_max_lon(collection['ways'][0])
        for i in range(1, len(collection['ways'])):
            way_max = self.get_way_max_lon(collection['ways'][i])
            if way_max > max:
                max = way_max
        return max

    def get_collection_min_lon(self, collection):
        min = self.get_way_min_lon(collection['ways'][0])
        for i in range(1, len(collection['ways'])):
            way_min = self.get_way_min_lon(collection['ways'][i])
            if way_min < min:
                min = way_min
        return min

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

    def get_collection_segments(self, collection):
        segments = []
        for way in collection['ways']:
            for segment in way['segments']:
                segments.append(segment)
        return segments

    def get_collection_curvature(self, collection):
        total = 0
        for way in collection['ways']:
            total += self.get_way_curvature(way)
        return total

    def get_way_curvature(self, way):
        # Use an already-summed value if it exists on the way.
        if 'curvature' in way:
            return way['curvature']
        # If not, sum the values of the segments
        else:
            total = 0
            for segment in way['segments']:
                if 'curvature' in segment:
                    total += segment['curvature']
            return total

    def get_collection_length(self, collection):
        total = 0
        for way in collection['ways']:
            total += self.get_way_length(way)
        return total

    def get_way_length(self, way):
        # Use an already-summed value if it exists on the way.
        if 'length' in way:
            return way['length']
        # If not, sum the values of the segments
        else:
            total = 0
            for segment in way['segments']:
                total += segment['length']
            return total

    def get_length_weighted_collection_tags(self, collection, tag, value_if_empty=None):
        values = {}
        for way in collection['ways']:
            if tag in way['tags']:
                value = way['tags'][tag]
            elif value_if_empty:
                value = value_if_empty
            else:
                value = None
            if value != None:
                if not value in values:
                    values[value] = 0
                values[value] += self.get_way_length(way)
        return sorted(values, key=values.__getitem__, reverse=True)

    def get_shared_collection_refs(self, collection):
        # If the first way doesn't have a ref tag, there is no way there will
        # be one shared by all ways.
        if not 'ref' in collection['ways'][0]['tags']:
            return set()

        # Beginning with the refs on our first way, check each way to find the refs
        # that are common to all.
        shared_refs = set(collection['ways'][0]['tags']['ref'].split(';'))
        for i in range(1, len(collection['ways'])):
            # If the any way doesn't have a ref tag, there is no way there will
            # be one shared by all ways.
            if not 'ref' in collection['ways'][i]['tags']:
                return set()

            # Reduce our shared_refs set to only those also in the next way.
            shared_refs = shared_refs & set(collection['ways'][i]['tags']['ref'].split(';'))
            # No need to look further if we have no shared_refs
            if not shared_refs:
                return shared_refs
        return shared_refs

    def get_collection_name(self, collection):
        names = self.get_length_weighted_collection_tags(collection, 'name')
        # See if we have any shared route-numbers.
        refs = sorted(self.get_shared_collection_refs(collection))
        if refs:
            ref = ' / '.join(refs)
        else:
            ref = None
        if names and ref:
            return '{} ({})'.format(names[0], ref)
        elif ref:
            return '{}'.format(ref)
        elif names:
            return '{}'.format(names[0])
        else:
            return '{}'.format(collection['ways'][0]['id'])

    def get_collection_description(self, collection):
        curvature = self.get_collection_curvature(collection)
        length = self.get_collection_length(collection)
        if self.units == 'km':
            description = 'Curvature: %.2f\nDistance: %.2f km\n' % (curvature, length / 1000)
        else:
            description = 'Curvature: %.2f\nDistance: %.2f mi\n' % (curvature, length / 1609)

        highway_tags = self.get_length_weighted_collection_tags(collection, 'highway')
        surface_tags = self.get_length_weighted_collection_tags(collection, 'surface', 'unknown')
        description = description + 'Type: %s\nSurface: %s\n' % (', '.join(highway_tags), ', '.join(surface_tags))
        description = description + '\nConstituent ways - <em>Open/edit in OpenStreetMap:</em>\n%s\n\n%s\n' % (self.get_constituent_list(collection), self.get_all_josm_link(collection))
        return '<div style="width: 500px">%s</div>' % (description.replace('\n', '<br/>'))

    def get_all_josm_link(self, collection):
        select = []
        for way in collection['ways']:
            select.append('way%d' % way['id'])
        josm_url ='http://127.0.0.1:8111/load_and_zoom?left=%.5f&right=%.5f&top=%.5f&bottom=%.5f&select=%s' % (self.get_collection_min_lon(collection) - 0.001, self.get_collection_max_lon(collection) + 0.001, self.get_collection_max_lat(collection) + 0.001, self.get_collection_min_lat(collection) - 0.001, ','.join(select))
        josm_link = '<a href="" onclick="var img=document.createElement(\'img\'); img.style.display=\'none\'; img.src=\'%s\'; this.parentElement.appendChild(img); return false;">Edit all in JOSM</a>' % (josm_url)
        coords_lat = ((self.get_collection_max_lat(collection) - self.get_collection_min_lat(collection))/2) + self.get_collection_min_lat(collection)
        coords_lon = ((self.get_collection_max_lon(collection) - self.get_collection_min_lon(collection))/2) + self.get_collection_min_lon(collection)
        coords = '<a href="" onclick="if (this.nextSibling.style.display==\'inline\') {this.nextSibling.style.display=\'none\';} else { this.nextSibling.style.display=\'inline\'; this.nextSibling.select() } return false;">coords </a><input type="text" style="display: none;" value="%.5f,%.5f"/>' % (coords_lon, coords_lat)
        return josm_link + ', ' + coords

    def get_constituent_list(self, collection):
        list = '<table style="width: 100%; text-align: center;">'
        list += '<tr><th>View</th><th>Surface</th><th>Curv.</th><th>Length</th><th>Name</th><th>Actions</th></tr>'
        for way in collection['ways']:
            view_link = '<a href="https://www.openstreetmap.org/way/%d">%d</a>' % (way['id'], way['id'])
            josm_url = 'http://127.0.0.1:8111/load_and_zoom?left=%.5f&right=%.5f&top=%.5f&bottom=%.5f&select=way%d' % (self.get_way_min_lon(way) - 0.001, self.get_way_max_lon(way) + 0.001, self.get_way_max_lat(way) + 0.001, self.get_way_min_lat(way) - 0.001, way['id'])
            josm_link = '<a href="" onclick="var img=document.createElement(\'img\'); img.style.display=\'none\'; img.src=\'%s\'; this.parentElement.appendChild(img); return false;">Edit in JOSM</a>' % (josm_url)
            coords_lat = ((self.get_way_max_lat(way) - self.get_way_min_lat(way))/2) + self.get_way_min_lat(way)
            coords_lon = ((self.get_way_max_lon(way) - self.get_way_min_lon(way))/2) + self.get_way_min_lon(way)
            web_edit_url = 'https://www.openstreetmap.org/edit?way=%d#map=16/%.4f/%.4f' % (way['id'], coords_lat, coords_lon)
            web_edit_link = '<a href="%s">Web Edit</a>' % (web_edit_url)
            coords = '<a href="" onclick="if (this.nextSibling.style.display==\'block\') {this.nextSibling.style.display=\'none\';} else { this.nextSibling.style.display=\'block\'; this.nextSibling.select() } return false;">coords</a><input type="text" style="display: none;" value="%.5f,%.5f"/>' % (coords_lon, coords_lat)
            if 'surface' in way['tags']:
                surface = way['tags']['surface']
            else:
                surface = 'unknown'
            if 'name' in way['tags']:
                name = way['tags']['name']
            else:
                name = ''
            curvature = '%.0f' % self.get_way_curvature(way)
            if self.units == 'km':
                length = '%.2f km\n' % (self.get_way_length(way) / 1000)
            else:
                length = '%.2f mi\n' % (self.get_way_length(way) / 1609)
            list += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s, %s, %s</td></tr>' % (view_link, surface, curvature, length, name, web_edit_link, josm_link, coords)

        list += '</table>'
        return list


    def get_collection_paved_style(self, collection):
        # Go by the highway tag first.
        highway_tags = self.get_length_weighted_collection_tags(collection, 'highway')
        if highway_tags[0] in self.assumed_paved_highways:
            return 'paved'
        # Then by the surface tag.
        surface_tags = self.get_length_weighted_collection_tags(collection, 'surface', 'unknown')
        if surface_tags[0] in self.paved_surfaces:
            return 'paved'
        elif surface_tags[0] == 'unknown':
            return 'unknown'
        else:
            return 'unpaved'

class KmlOutput(object):
    no_compress = False
    description = "Curvature data is a derivative of Open Street Map which is © OpenStreetMap contributors and provided under the terms of the Open Data Commons Open Database License (ODbL). https://www.openstreetmap.org/about"

    def __init__(self, units):
        self.tools = OutputTools(units)

    def _write_header(self, f):
        self._write_doc_start(f)
        self._write_styles(f, self.get_styles())

    def _write_doc_start(self, f):
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')
        f.write('<Document>\n')
        f.write('	<description>{}</description>\n'.format(self.description))

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
                style['width'] = '3'
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

    def _record_collection_bbox(self, collection):
        for way in collection['ways']:
            if not hasattr(self, 'min_lat') and 'segments' in way and len(way['segments']):
                self.min_lat = way['segments'][0]['start'][0]
                self.max_lat = way['segments'][0]['start'][0]
                self.min_lon = way['segments'][0]['start'][1]
                self.max_lon = way['segments'][0]['start'][1]
            way_max_lat = self.tools.get_way_max_lat(way)
            if way_max_lat > self.max_lat:
                self.max_lat = way_max_lat
            way_min_lat = self.tools.get_way_min_lat(way)
            if way_min_lat < self.min_lat:
                self.min_lat = way_min_lat
            way_max_lon = self.tools.get_way_max_lon(way)
            if way_max_lon > self.max_lon:
                self.max_lon = way_max_lon
            way_min_lon = self.tools.get_way_min_lon(way)
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

    def head (self, f):
        self._write_header(f)

    def write_collection(self, f, collection):
        self._record_collection_bbox(collection)
        self._write_collection(f, collection)

    def get_collection_description(self, collection):
        return self.tools.get_collection_description(collection)

    def foot (self, f):
        self._write_region(f)
        self._write_footer(f)


class SingleColorKmlOutput(KmlOutput):

    min_curvature = 0
    max_curvature = 4000

    def __init__(self, units, min_curvature, max_curvature, assumed_paved_highways=None, paved_surfaces=None):
        super(SingleColorKmlOutput, self).__init__(units)
        self.tools = OutputTools(units, assumed_paved_highways, paved_surfaces)
        self.min_curvature = min_curvature
        self.max_curvature = max_curvature

    def head(self, f):
        super(SingleColorKmlOutput, self).head(f)
        f.write('<ScreenOverlay id="curvature_key">\n')
        f.write('	<name>Legend</name>\n')
        f.write('	<Icon><href>images/legend.png</href></Icon>\n')
        f.write('	<overlayXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n')
        f.write('	<screenXY x="25" y="95" xunits="pixels" yunits="pixels"/>\n')
        f.write('	<rotationXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>\n')
        f.write('	<size x="0" y="0" xunits="pixels" yunits="pixels"/>\n')
        f.write('	<visibility>1</visibility>\n')
        f.write('</ScreenOverlay>\n')
        f.write('<Folder>\n')
        f.write('	<name>Roads</name>\n')

    def foot(self, f):
        f.write('</Folder>\n')
        super(SingleColorKmlOutput, self).foot(f)

    def get_styles(self):
        styles = {'paved0':{'color':'F000E010'}} # Straight roads
        styles = {'unpaved0':{'color':'F000E010', 'width': '2'}} # Straight roads
        styles = {'unknown0':{'color':'7F00E010', 'width': '2.5'}} # Straight roads

        # Add a style for each level in a gradient from yellow to red (00FFFF - 0000FF)
        for i in range(256):
            styles['paved{}'.format(i + 1)] = {'color':'F000{:02X}FF'.format(255 - i)}
            styles['unpaved{}'.format(i + 1)] = {'color':'F000{:02X}FF'.format(255 - i), 'width': '2'}
            styles['unknown{}'.format(i + 1)] = {'color':'7f00{:02X}FF'.format(255 - i), 'width': '2.5'}

        # Add a style for each level in a gradient from red to magenta (0000FF - FF00FF)
        for i in range(1, 256):
            styles['paved{}'.format(i + 256)] = {'color':'F0{:02X}00FF'.format(i)}
            styles['unpaved{}'.format(i + 256)] = {'color':'F0{:02X}00FF'.format(i), 'width': '2'}
            styles['unknown{}'.format(i + 256)] = {'color':'7f{:02X}00FF'.format(i), 'width': '2.5'}

        return styles

    def _write_collection(self, f, collection):
        segments = self.tools.get_collection_segments(collection)
        if not len(segments):
# 				sys.stderr.write("\nError: way has no segments: {} \n".format(way['name']))
            return
        f.write('	<Placemark>\n')
        f.write('		<styleUrl>#' + self.get_collection_line_style(collection) + '</styleUrl>\n')
        f.write('		<name>' + escape(self.tools.get_collection_name(collection)) + '</name>\n')
        f.write('		<description><![CDATA[' + self.get_collection_description(collection) + ']]></description>\n')
        f.write('		<LineString>\n')
        f.write('			<tessellate>1</tessellate>\n')
        f.write('			<coordinates>')
        self._write_segments(f, segments);
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

    def get_collection_line_style(self, collection):
        return '{}{}'.format(
            self.tools.get_collection_paved_style(collection),
            self.level_for_curvature(self.tools.get_collection_curvature(collection)))


class MultiColorKmlOutput(KmlOutput):

    def head(self, f):
        super(MultiColorKmlOutput, self).head(f)
        f.write('	<Style id="folderStyle">\n')
        f.write('		<ListStyle>\n')
        f.write('			<listItemType>checkHideChildren</listItemType>\n')
        f.write('		</ListStyle>\n')
        f.write('	</Style>\n')

    def _write_collection(self, f, collection):
        segments = self.tools.get_collection_segments(collection)

        f.write('	<Folder>\n')
        f.write('		<styleUrl>#folderStyle</styleUrl>\n')
        f.write('		<name>' + escape(self.tools.get_collection_name(collection)) + '</name>\n')
        f.write('		<description><![CDATA[' + self.get_collection_description(collection) + ']]></description>\n')
        current_curvature_level = 0
        i = 0
        for segment in segments:
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

    def get_collection_line_style(self, collection):
        if 'surface' in collection['ways'][0]['tags']:
            return collection['ways'][0]['tags']['surface']
        else:
            return 'unknown'

    def _write_collection(self, f, collection):
        for way in collection['ways']:
            super(SurfaceKmlOutput, self)._write_collection(f, {'join_type': 'none', 'ways': [way]})

    def get_collection_description(self, collection):
        if 'highway' in collection['ways'][0]['tags']:
            highway = collection['ways'][0]['tags']['highway']
        else:
            highway = ''
        if 'surface' in collection['ways'][0]['tags']:
            surface = collection['ways'][0]['tags']['surface']
        else:
            surface = 'unknown'
        description = 'Type: %s\nSurface: %s\n' % (highway, surface)
        description = description + '\nConstituent ways - <em>Open/edit in OpenStreetMap:</em>\n%s\n' % (self.tools.get_constituent_list(collection))
        return '<div style="width: 500px">%s</div>' % (string.replace(description, '\n', '<br/>'))

    def get_filename(self, basename, extension):
        filename = basename + '.surfaces'
        if self.filter.min_length > 0 or self.filter.max_length > 0:
            filename += '.l_{0:.0f}'.format(self.filter.min_length)
        if self.filter.max_length > 0:
            filename += '-{0:.0f}'.format(self.filter.max_length)
        filename += self._filename_suffix() + '.' + extension
        return filename;
