from curvature.radiusmath import circum_circle_radius 

def test_circum_circle_radius_zero_lengths():
  assert circum_circle_radius(0, 0, 0) == 10000

def test_circum_circle_radius_zero_division():
  assert circum_circle_radius(0.13430093277996386, 0.13430093277996386, 0.2686018655599277) == 10000