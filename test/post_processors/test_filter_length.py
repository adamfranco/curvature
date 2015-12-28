from curvature.post_processors.filter_length import FilterLength

def test_filter_length_min():
	data = [
		{'length': 2},
		{'length': 5},
		{'length': 6},
	]
	result = list(FilterLength(min=5).process(data))
	assert(result == [{'length': 5}, {'length': 6}])


def test_filter_length_max():
	data = [
		{'length': 2},
		{'length': 5},
		{'length': 6},
	]
	result = list(FilterLength(max=5).process(data))
	assert(result == [{'length': 2}, {'length': 5}])


def test_filter_length_min_max():
	data = [
		{'length': 2},
		{'length': 5},
		{'length': 6},
	]
	result = list(FilterLength(min=5, max=5).process(data))
	assert(result == [{'length': 5}])