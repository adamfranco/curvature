curvature.py
============

Find roads that are the most curved or twisty based on Open Street Map (OSM) data.

The goal of this script is to help those who enjoy twisty roads (such as 
motorcycle or driving enthusiasts) to find promising roads that are not well known.
It works by calculating a synthetic "curvature" parameter for each road segment
(known as a "way" in OSM parlance) that represents how twisty that segment is. 
These twisty segments can then be output as KML files that can be viewed in Google Earth
or viewed in tabular form.


About the "curvature" parameter:
--------------------------------
The "curvature" of a way is determined by calculating the ratio of the traveled distance
to hypotenuse for every sequence of three points, then adding all of the ratios.
Sharp curves will have a travelled-distance much greater than the hypotenuse 
(as well as many coordinate points for a given distance) and will rack up "curvature"
much faster than straight roads where there is very little difference between the
traveled distance and the hypotenuse.

The current curvature parameter is certainly not ideal and suggestions for improvement
are welcome.

About & License
---------------
Author: Adam Franco  
[https://github.com/adamfranco/curvature](https://github.com/adamfranco/curvature)  
Copyright 2012 Adam Franco  
License: GNU General Public License Version 3 or later  

Installation
============

This is a Python script, therefore you need a functional Python environment on your computer. See
http://python.org/

curvature.py makes use of the imposm.parser which you can find at
[dev.omniscale.net/imposm.parser](http://dev.omniscale.net/imposm.parser/)

Once your Python environment set up and the imposm.parser module installed, just download the
curvature.py script and run it. There is no installation needed.

Usage
=====

curvature.py works with Open Street Map (OSM) XML data files. While you can export these from a
small area directly from [openstreetmap.org](http://www.openstreetmap.org/) , you are limited to a
small area with a limited number of points so that you don't overwelm the OSM system. A better
alternative is to download daily exports of OSM data for your region from
[Planet.osm](https://wiki.openstreetmap.org/wiki/Planet.osm).

This script was developed using downloads of the US state OSM data provided at:
[download.geofabrik.de/openstreetmap](http://download.geofabrik.de/openstreetmap/north-america/us/)

Once you have downloaded a .osm file that you wish to work with, you can run curvature.py with its
default options:

<code>./curvature.py vermont.osm</code>

This will generate a vermont.osm.kml file that includes red lines for all of the matched segments
and output the matched segments in tabular for as well.

Use

<code>./curvature.py -h</code>

for more options