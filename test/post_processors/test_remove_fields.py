from curvature.post_processors.remove_fields import RemoveFields

def test_remove_fields():
	data = [
		{
			'name': 'foo',
			'length': 5,
			'curvature': 3
		},
		{
			'name': 'bar',
			'length': 5,
			'curvature': 7
		},
	]
	result = list(RemoveFields(fields=['length', 'name']).process(data))
	result_item = result[0]
	assert(result == [{'curvature': 3}, {'curvature': 7}])
