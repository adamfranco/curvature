from curvature.post_processors.filter_curvature import FilterCurvature

def test_filter_curvature_min():
	data = [
		{'curvature': 2},
		{'curvature': 5},
		{'curvature': 6},
	]
	result = list(FilterCurvature(min=5).process(data))
	assert(result == [{'curvature': 5}, {'curvature': 6}])


def test_filter_curvature_max():
	data = [
		{'curvature': 2},
		{'curvature': 5},
		{'curvature': 6},
	]
	result = list(FilterCurvature(max=5).process(data))
	assert(result == [{'curvature': 2}, {'curvature': 5}])


def test_filter_curvature_min_max():
	data = [
		{'curvature': 2},
		{'curvature': 5},
		{'curvature': 6},
	]
	result = list(FilterCurvature(min=5, max=5).process(data))
	assert(result == [{'curvature': 5}])