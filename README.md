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
The "curvature" of a way is determined by iterating over every set of three points
in the line. Each set of three points form a triangle and that triangle has a circumcircle
whose radius corresponds to the radius of the curve for that set. Since every line
segment (between two points) is part of two separate triangles, the radius of the curve
at that segment is considdered to be the average of the radii for its member sets.
Now that we have a curve radius for each segment we can categorize each segment into
ranges of radii from very tight (short radius turn) to very broad or straight (long radius turn).
Once each segment is categorized its length can be multiplied by a weighting (by default
zero for straight segments, 1 for broad curves, and up to 2 for the tightest curves).
The sum of all of these weighting gives us a number for curvature that corresponds
proportionally to the distance (in meters) that you will be in a turn.*

* If all weights are 1 then the curvature parameter will be exactly the distance
  in turns. The goal of this project however is to prefer tighter turns, so sharp
  corners are given an increased weight.

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

This will generate a vermont.osm.kml file that includes lines for all of the matched segments
and output the matched segments in tabular for as well.

Use

<code>./curvature.py -h</code>

for more options.

KML Output
----------

Open the KML files in Google Earth. The color-coding is as follows: straight segments are green and the four levels of curves are color-coded from yellow to red with decreasing turn radii.