# Function Examples - Demonstrating RLangC function features

# Simple function without type annotations
def greet(name):
    return "Hello, " + name

print(greet("World"))

# Function with type annotations
def add(x: int, y: int) -> int:
    return x + y

print("5 + 3 = " + str(add(5, 3)))

# Function with default parameters
def power(base: float, exponent: float = 2.0) -> float:
    return base ** exponent

print("2^3 = " + str(power(2.0, 3.0)))
print("3^2 = " + str(power(3.0)))  # Uses default exponent

# Recursive function
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print("5! = " + str(factorial(5)))

# Function with multiple return paths
def classify_number(n: int) -> str:
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print("classify_number(-5): " + classify_number(-5))
print("classify_number(0): " + classify_number(0))
print("classify_number(10): " + classify_number(10))

# Higher-order function concept
def apply_operation(x: int, y: int, operation):
    return operation(x, y)

def multiply(a: int, b: int) -> int:
    return a * b

result = apply_operation(4, 5, multiply)
print("4 * 5 = " + str(result))
