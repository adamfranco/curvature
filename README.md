![Vermont Route 17](http://www2.adamfranco.com/curvature/images/Page_Mill_Rd.jpg)

Curvature
============

Find roads that are the most curved or twisty based on [Open Street Map](http://www.openstreetmap.org/) (OSM) data.

The goal of this program is to help those who enjoy twisty roads (such as
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

Rendered Data
-------------
Rendered curvature files generated with this program can be dowloaded from [adamfranco.com/curvature/kml/](http://www2.adamfranco.com/curvature/kml/). Files are available for the entire world and are automatically updated approximately every two weeks.

Examples
--------
Below are links to some example KML files generated with Curvature. Additional files can
be found at [adamfranco.com/curvature/kml/](http://www2.adamfranco.com/curvature/kml/).

* Pre-processing the [vermont-latest.osm.pbf](http://download.geofabrik.de/north-america/us/vermont-latest.osm.pbf) file.

      ./curvature-calculate -v vermont-latest.osm.pbf \
        | ./curvature-pp add_length \
        | ./curvature-pp sort --key curvature --direction DESC \
        > vermont.msgpack

* A basic KML file generated with a minimum curvature of 300 using the pre-processed
  [vermont-latest.osm.pbf](http://download.geofabrik.de/north-america/us/vermont-latest.osm.pbf)
  file (above).

  This file includes all ways in the input file that have a curvature value greater than 300
  and are not marked as unpaved. As mentioned above, a curvature of 300 this means that these
  ways have at least 150 meters of tight curves with a radius of less than 30 meters, 300 meters
  of gentle curves with a radius less than 175 meters, or a combination thereof.

  In practice, a curvature of 300 is useful for finding roads that might be a bit fun
  in a sea of otherwise bland options. While more curvy roads will also be included, roads
  in the 300-600 range tend to be pleasant rather than exciting.

      cat vermont.msgpack \
        | ./curvature-pp filter_collections_by_curvature --min 300 \
        | ./curvature-output-kml --min_curvature 300 --max_curvature 20000 \
        > vermont.c_300.kml

  [vermont.c_300.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_300.kmz)

  An additional note: Vermont has approximately [8,000 miles of dirt roads and only 6,000 miles
of paved roads](http://www.nytimes.com/1996/06/24/us/in-slow-paced-vermont-the-dirt-road-reigns.html).
  At the time of this writing most of the dirt roads were not tagged as such in Open Street
  Map, leading to the inclusion of many dirt roads in the KML file above. I have tagged
  many of the roads in my region with appropriate 'surface' tags, but there is more to be done.
  Head to [openstreetmap.org](http://www.openstreetmap.org/) and help tag roads with appropriate
  surfaces so that we can better filter our results.

* A basic KML file generated with a minimum curvature of 1000 using the pre-processed
  [vermont-latest.osm.pbf](http://download.geofabrik.de/north-america/us/vermont-latest.osm.pbf)
  file (above).

  This file includes all ways in the input file that have a curvature value greater than 1000
  and are not marked as unpaved. As mentioned above, a curvature of 1000 this means that these
  ways have at least 500 meters of tight curves with a radius of less than 30 meters, 1000 meters
  of gentle curves with a radius less than 175 meters, or a combination thereof.

  In practice a minimum curvature of 1000 is useful for finding the best roads in a region.
  There will be many roads that are quite fun but don't quite make the cut, but all of the
  roads listed will be very curvy.

      cat vermont.msgpack \
        | ./curvature-pp filter_collections_by_curvature --min 1000 \
        | ./curvature-output-kml --min_curvature 1000 --max_curvature 20000 \
        > vermont.c_1000.kml

  [vermont.c_1000.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_1000.kmz)

* Multi-colored KML files generated with a minimum curvature of 1000 using the pre-processed
  [vermont-latest.osm.pbf](http://download.geofabrik.de/north-america/us/vermont-latest.osm.pbf)
  file (above).

  This file colors the ways listed in the second example based on curve radius.
  Zoom on corners to see the shading. Green segments do not contribute to the 'curvature' value
  while yellow, orange, and red segments do.

      cat vermont.msgpack \
        | ./curvature-pp filter_collections_by_curvature --min 1000 \
        | ./curvature-output-kml-curve-radius \
        > vermont.c_1000.curves.kml

  [vermont.c_1000.curves.kml](http://www2.adamfranco.com/curvature/kml/north_america/us/vermont.c_1000.curves.kmz)  

* All of the commands above, combined into a single script `processing_chains/adams_defaults.sh`:

      mv vermont-latest.osm.pbf vermont.osm.pbf
      ./processing_chains/adams_defaults.sh -v vermont.osm.pbf

* More examples can be seen at [adamfranco.com/curvature/kml/](http://www2.adamfranco.com/curvature/kml/)

Installation
============

Prerequisites
-------------

*Python*
This is a Python script, therefore you need a functional Python 2.7 or later environment on your computer. See
http://python.org/

*Protocol Buffers*
The `imposm.parser` library (below) utilizes the ["Protocol Buffers" library](https://developers.google.com/protocol-buffers/docs/downloads)
to read `.pbf` files. You will need to download and install the Protocol Buffers library. This can usually be accomplished with something like:

    cd /usr/local/src/
    wget https://github.com/google/protobuf/releases/download/v2.6.1/protobuf-2.6.1.tar.gz
    tar xzf protobuf-2.6.1.tar.gz
    cd protobuf-2.6.1
    ./configure
    make
    make check
    make install

*imposm.parser*
curvature makes use of the `imposm.parser` which you can find at
[imposm.org](http://imposm.org/docs/imposm.parser/latest/install.html#installation) and installed
with `pip` or `easy_install`:

    pip install imposm.parser

or

    easy_install imposm.parser

*msgpack*
curvature makes use of `msgpack` which you can find at
[python.org](https://pypi.python.org/pypi/msgpack-python) and installed
with `pip` or `easy_install`:

    pip install msgpack-python

or

    easy_install msgpack-python

Curvature Installation
----------------------
Once your Python environment set up and the `imposm.parser` and `msgpack-python` modules are installed, just download
Curvature and run it:

    git clone https://github.com/adamfranco/curvature.git
    cd curvature
    ./curvature-calculate --help

Usage
=====
Curvature works with Open Street Map (OSM) XML data files. While you can export these from a
small area directly from [openstreetmap.org](http://www.openstreetmap.org/) , you are limited to a
small area with a limited number of points so that you don't overwhelm the OSM system. A better
alternative is to download daily exports of OSM data for your region from
[Planet.osm](https://wiki.openstreetmap.org/wiki/Planet.osm).

This script was developed using downloads of the US state OSM data provided at:
[download.geofabrik.de/openstreetmap](http://download.geofabrik.de/openstreetmap/north-america/us/)

Once you have downloaded a .osm file that you wish to work with, you can run one of the the predefined processing changes with their default options:

    ./processing_chains/adams_defaults.sh -v vermont.osm.pbf

This will generate a set of compressed KMZ files that includes lines for all of the matched segments.

Use

    ./processing_chains/adams_defaults.sh -h

for more options.

Basic KML Output
----------
Open the KML files in Google Earth. GoogleEarth can become overloaded with giant KML files, so the
default mode is to generate a single placemark for each matching way that has a single-color
line-string. On a reasonably modern computer even large files such as roads with curvature greater
than 300 in California can be rendered when formatted in this way.

Colored-curves KML Output
--------------------
Additionally, this script allows rendering of ways as a sequence of segments color-coded based on
the curvature of each segment. These 'colorized' KML files provide a neat look at the radius of turns and are especially useful when tuning the radii and weights for each level to adjust which ways are matched. The color-coding is as follows: straight segments are green and the four levels of curves are color-coded from yellow to red with decreasing turn radii.

Unfortunately, these multi-colored ways are significantly more difficult for GoogleEarth to render
than the longer single-color segments, so try to avoid files larger than about 40MB. Google Earth
can easily handle smaller areas like Vermont with a curvature of 300, but larger regions (like
California) may need to be trimmed down with a bounding box if you wish to make usable multicolor
KML files.

Building your own processing scripts
--------------------
The processing-chains in `curvature/processing_chains/` are just a few examples of ways to use this
program. You can easily pipe output from one filter to the next to modify the data stream to your liking.

@todo *Add more detail on writing filters and processing sequences.*
