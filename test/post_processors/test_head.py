from curvature.post_processors.head import Head

def test_head():
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
	result = list(Head(num=2).process(data))
	assert(len(result) == 2)
