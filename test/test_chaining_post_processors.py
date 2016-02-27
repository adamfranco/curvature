from curvature.post_processors.filter_curvature import FilterCurvature
from curvature.post_processors.head import Head
def test_chaining_post_processors():
	head = Head(num=1)
	filter_curvature = FilterCurvature(min=5)
	data = [
		{'curvature': 2},
		{'curvature': 5},
		{'curvature': 6},
	]
	chain = reduce(lambda acc, processor: processor.process(acc), [data, filter_curvature, head])
	result = list(chain)
	assert(result == [{'curvature': 5}])
