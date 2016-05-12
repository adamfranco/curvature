from curvature.post_processors.add_length import AddLength

def test_add_length():
	first = {
		'length': 2,
	}
	second = {
		'length': 4,
	}
	third = {
		'length': 5,
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
	result = list(AddLength().process(data))
	result_item = result[0]
	assert(result_item['length'] == 11)
