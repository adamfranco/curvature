from curvature.post_processors.sort import Sort

def test_add_length():
	first = {
		'length': 7,
	}
	second = {
		'length': 4,
	}
	third = {
		'length': 5,
	}
	data = [
		first,
		second,
		third,
	]
	result = list(Sort(key='length').process(data))
	assert([entry['length'] for entry in result] == [4,5,7])


def test_add_length_reverse():
	first = {
		'length': 7,
	}
	second = {
		'length': 4,
	}
	third = {
		'length': 5,
	}
	data = [
		first,
		second,
		third,
	]
	result = list(Sort(key='length', reverse=True).process(data))
	assert([entry['length'] for entry in result] == [7, 5, 4])
