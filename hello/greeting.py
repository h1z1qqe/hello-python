def greet(name: str) -> str:
    return f"Hello, {name}!"


def sum_range(from_: int, to: int) -> int:
    return sum(range(from_, to + 1))

def factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result