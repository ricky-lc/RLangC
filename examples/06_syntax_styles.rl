# Demonstrating both syntax styles - indentation and braces

# Style 1: Indentation-based (Python-like)
def fibonacci_indent(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci_indent(n - 1) + fibonacci_indent(n - 2)

# Style 2: Brace-based (C-like)
def fibonacci_braces(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci_braces(n - 1) + fibonacci_braces(n - 2)
}

# Both produce the same results
print("Fibonacci (indent style):")
let i = 0
while i < 8:
    print(str(fibonacci_indent(i)))
    i += 1

print("Fibonacci (brace style):")
let j = 0
while j < 8 {
    print(str(fibonacci_braces(j)))
    j += 1
}

# Mixed style example - choose what works best
def calculate_stats(numbers) {
    let sum = 0
    let count = 0
    
    for num in numbers:
        sum += num
        count += 1
    
    let average = sum / count
    return average
}

let data = [10, 20, 30, 40, 50]
print("Average: " + str(calculate_stats(data)))
