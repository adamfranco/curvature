# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from curvature import geomath

def test_distance_on_earth_short_distance():
  assert geomath.distance_on_unit_sphere(47.86242430000005, 7.8065880000000005, 47.86242420000014, 7.806588099999998) == 0
