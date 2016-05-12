from curvature.post_processors.filter_type import FilterType

def test_filter_type_include():
  data = [
    {'type': 'a'},
    {'type': 'b'},
    {'type': 'c'},
  ]
  result = list(FilterType(include_types=['a', 'b']).process(data))
  assert(result == [{'type': 'a'}, {'type': 'b'}])

def test_filter_type_exclude():
  data = [
    {'type': 'a'},
    {'type': 'b'},
    {'type': 'c'},
  ]
  result = list(FilterType(exclude_types=['a', 'b']).process(data))
  assert(result == [{'type': 'c'}])

def test_filter_type_no_filter():
  data = [
    {'type': 'a'}
  ]
  result = list(FilterType().process(data))
  assert(result == [])
