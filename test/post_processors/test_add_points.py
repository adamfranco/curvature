from curvature.post_processors.add_points import AddPoints

def test_add_points():
	first = {
		'start': [1,1],
		'end': [2,2]
	}
	second = {
		'start': [2,2],
		'end': [3,3]
	}
	third = {
		'start': [3,3],
		'end': [4,4]
	}
	item = {
		'segments': 
		[
			first,
			second,
			third,
		]
	}
	data = [item]
	result = list(AddPoints().process(data))
	result_item = result[0]
	assert(result_item['points'] == [(1,1), (2,2), (3,3), (4,4)])
