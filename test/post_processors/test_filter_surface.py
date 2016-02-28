from curvature.post_processors.filter_surface import FilterSurface

def test_filter_surface_include():
  data = [
    {'surface': 'a'},
    {'surface': 'b'},
    {'surface': 'c'},
  ]
  result = list(FilterSurface(include_surfaces=['a', 'b']).process(data))
  assert(result == [{'surface': 'a'}, {'surface': 'b'}])

def test_filter_surface_exclude():
  data = [
    {'surface': 'a'},
    {'surface': 'b'},
    {'surface': 'c'},
  ]
  result = list(FilterSurface(exclude_surfaces=['a', 'b']).process(data))
  assert(result == [{'surface': 'c'}])

def test_filter_surface_no_filter():
  data = [
    {'surface': 'a'}
  ]
  result = list(FilterSurface().process(data))
  assert(result == [])
