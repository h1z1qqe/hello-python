from hello.greeting import factorial, greet, sum_range

def test_greet():
    assert greet("Python") == "Hello, Python!"
    assert greet("CI") == "Hello, CI!"


def test_sum_range():
    assert sum_range(1, 10) == 55
    assert sum_range(1, 100) == 5050

def test_factorial():
    assert factorial(0) == 1
    assert factorial(5) == 120