![Vermont Route 17](http://www2.adamfranco.com/curvature/images/Page_Mill_Rd.jpg)

curvature.py
============

Find roads that are the most curved or twisty based on [Open Street Map](http://www.openstreetmap.org/) (OSM) data.

The goal of this script is to help those who enjoy twisty roads (such as 
motorcycle or driving enthusiasts) to find promising roads that are not well known.
It works by calculating a synthetic "curvature" parameter for each road segment
(known as a "way" in OSM parlance) that represents how twisty that segment is. 
These twisty segments can then be output as KML files that can be viewed in Google Earth
or viewed in tabular form.


About the "curvature" parameter:
--------------------------------
The "curvature" of a way is determined by iterating over every set of three points
in the line. Each set of three points form a triangle and that triangle has a circumcircle
whose radius corresponds to the radius of the curve for that set. Since every line
segment (between two points) is part of two separate triangles, the radius of the curve
at that segment is considered to be the average of the radii for its member sets.
Now that we have a curve radius for each segment we can categorize each segment into
ranges of radii from very tight (short radius turn) to very broad or straight (long radius turn).
Once each segment is categorized its length can be multiplied by a weight to increase the 
influence of the most curvy segments. By default a weight of 0 is given for straight segments, 
1 for broad curves, and up to 2 for the tightest curves. The sum of all of the weighted
lengths gives us a number for the curvature of the whole line that corresponds proportionally
to the distance (in meters) that you will be in a turn.*

\* If all weights are 1 then the curvature parameter will be exactly the distance in turns. 
The goal of this project however is to prefer tighter turns, so sharp corners are given an
increased weight.

About & License
---------------
Author: Adam Franco  
[https://github.com/adamfranco/curvature](https://github.com/adamfranco/curvature/wiki/)  
Copyright 2012 Adam Franco  
License: GNU General Public License Version 3 or later

Examples
--------
Below are links to some example KML files generated with curvature.py. Additional files can
be found at [adamfranco.com/curvature/](http://www2.adamfranco.com/curvature/).

* A basic KML file generated with default options using the
  [vermont.osm](http://download.geofabrik.de/openstreetmap/north-america/us/vermont.osm.bz2) 
  file (after unzipping). 
  
  This file includes all ways in the input file that have a curvature value greater than 300 
  and are not marked as unpaved. As mentioned above, a curvature of 300 this means that these 
  ways have at least 150 meters of tight curves with a radius of less than 30 meters, 300 meters 
  of gentle curves with a radius less than 175 meters, or a combination thereof.
  
  In practice, a curvature of 300 is useful for finding roads that might be a bit fun
  in a sea of otherwise bland options. While more curvy roads will also be included, roads
  in the 300-600 range tend to be pleasant rather than exciting.
  
  `./curvature.py -v vermont.osm`
  
  [vermont.c_300.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_300.kml)  
  [vermont-bristol.c_300.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont-bristol.c_300.kml)
  ([View in Google Maps](http://goo.gl/maps/T63Kv)) A nice [sub-set](http://www2.adamfranco.com/curvature/osm/vermont-bristol.osm) of this data.
  
  An additional note: Vermont has approximately [8,000 miles of dirt roads and only 6,000 miles
of paved roads](http://www.nytimes.com/1996/06/24/us/in-slow-paced-vermont-the-dirt-road-reigns.html).
  At the time of this writing most of the dirt roads were not tagged as such in Open Street
  Map, leading to the inclusion of many dirt roads in the KML file above. I have tagged
  many of the roads in my region with appropriate 'surface' tags, but there is more to be done.
  Head to [openstreetmap.org](http://www.openstreetmap.org/) and help tag roads with appropriate
  surfaces so that we can better filter our results.
  
* A basic KML file generated with a minimum curvature of 1000 using the
  [vermont.osm](http://download.geofabrik.de/openstreetmap/north-america/us/vermont.osm.bz2) 
  file (after unzipping). 
  
  This file includes all ways in the input file that have a curvature value greater than 1000 
  and are not marked as unpaved. As mentioned above, a curvature of 1000 this means that these 
  ways have at least 500 meters of tight curves with a radius of less than 30 meters, 1000 meters 
  of gentle curves with a radius less than 175 meters, or a combination thereof.
  
  In practice a minimum curvature of 1000 is useful for finding the best roads in a region.
  There will be many roads that are quite fun but don't quite make the cut, but all of the
  roads listed will be very curvy.
  
  `./curvature.py -v --min_curvature 1000 vermont.osm`
  
  [vermont.c_1000.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_1000.kml)  
  [vermont-bristol.c_1000.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont-bristol.c_1000.kml)
  ([View in Google Maps](http://goo.gl/maps/ZDh9u)) A nice [sub-set](http://www2.adamfranco.com/curvature/osm/vermont-bristol.osm) of this data.

* Multi-colored KML files generated with a minimum curvature of 300 and 1000 using the
  [vermont.osm](http://download.geofabrik.de/openstreetmap/north-america/us/vermont.osm.bz2) 
  file (after unzipping). 
  
  These files color the ways listed in the first and second examples based on curve radius. 
  Zoom on corners to see the shading. Green segments do not contribute to the 'curvature' value
  while yellow, orange, and red segments do.
  
  `./curvature.py -v --colorize --add_kml min_curvature=1000 vermont.osm`
  
  [vermont.c_300.multicolor.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_300.multicolor.kml) 
  [vermont.c_1000.multicolor.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_1000.multicolor.kml)  
  [vermont-bristol.c_300.multicolor.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont-bristol.c_300.multicolor.kml)
  ([View in Google Maps](http://goo.gl/maps/ItFNg)) A nice [sub-set](http://www2.adamfranco.com/curvature/osm/vermont-bristol.osm) of this data.

* A set of KML files of the roads in the San Francisco Bay area with a minimum curvature 
  of 1000 using the [california.osm](http://download.geofabrik.de/openstreetmap/north-america/us/california.osm.bz2) 
  file (after unzipping). 
  
  `./curvature.py -v --max_lat_bound 38.5 --min_lat_bound 36.5 --min_lon_bound -123.25 --max_lon_bound -121.0 --output_basename california-bay-area --min_curvature 1000 --add_kml colorize=1 california.osm`
  
   [california-bay-area.1000.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/california-bay-area.1000.kml) ([view in Google Maps](http://goo.gl/maps/uU1R9))  
   [california-bay-area.1000.multicolor.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/california-bay-area.1000.multicolor.kml)
   
   What a smorgasbord!

* More examples can be seen at [adamfranco.com/curvature/kml/](http://www2.adamfranco.com/curvature/kml/)

Installation
============

This is a Python script, therefore you need a functional Python 2.7 or later environment on your computer. See
http://python.org/

curvature.py makes use of the imposm.parser which you can find at
[dev.omniscale.net/imposm.parser](http://dev.omniscale.net/imposm.parser/)

Once your Python environment set up and the imposm.parser module installed, just download the
curvature.py script and run it. There is no installation needed.

Usage
=====
curvature.py works with Open Street Map (OSM) XML data files. While you can export these from a
small area directly from [openstreetmap.org](http://www.openstreetmap.org/) , you are limited to a
small area with a limited number of points so that you don't overwhelm the OSM system. A better
alternative is to download daily exports of OSM data for your region from
[Planet.osm](https://wiki.openstreetmap.org/wiki/Planet.osm).

This script was developed using downloads of the US state OSM data provided at:
[download.geofabrik.de/openstreetmap](http://download.geofabrik.de/openstreetmap/north-america/us/)

Once you have downloaded a .osm file that you wish to work with, you can run curvature.py with its
default options:

<code>./curvature.py -v vermont.osm</code>

This will generate a vermont.osm.kml file that includes lines for all of the matched segments.

Use

<code>./curvature.py -h</code>

for more options.

Basic KML Output
----------
Open the KML files in Google Earth. GoogleEarth can become overloaded with giant KML files, so the
default mode is to generate a single placemark for each matching way that has a single-color 
line-string. On a reasonably modern compter even large files such as roads with curvature greater 
than 300 in California can be rendered when formatted in this way.

Colored KML Output
--------------------
Additionally, this script allows rendering of ways as a sequence of segments color-coded based on
the curvature of each segment. These 'colorized' KML files provide a neat look at the radius of turns and are especially useful when tuning the radii and weights for each level to adjust which ways are matched. The color-coding is as follows: straight segments are green and the four levels of curves are color-coded from yellow to red with decreasing turn radii. 

Unfortunately, these multi-colored ways are significantly more difficult for GoogleEarth to render
than the longer single-color segments, so try to avoid files larger than about 40MB. Google Earth
can easily handle smaller areas like Vermont with a curvature of 300, but larger regions (like
California) may need to be trimmed down with a bounding box if you wish to make usable multicolor
KML files. 

Multiple KML Outputs
--------------------
Since KML generation is a tiny fraction of the overall execution time, you can use the `--add_kml` option to generate multiple KML files with different curvature limits, length limits, and color settings from the same parsing and calculation pass. Only curvature and length filters can be passed to `--add_kml` since road-surface and bounding-box filters are applied in the initial parsing pass. Still, the `--add_kml` option can allow you to generate several KML files at a time.

Tabular Output
--------------
You can pass the `-t` option (and optionally the `--no_kml` option) to output a tabular listing of the matching ways rather than generating KML files.
