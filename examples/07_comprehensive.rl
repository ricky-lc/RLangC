# Comprehensive Example - Combining Multiple Features

# Constants and configuration
const MAX_ITERATIONS = 100
const THRESHOLD: float = 0.001

# Helper function with type annotations
def is_prime(n: int) -> bool:
    if n < 2:
        return false
    if n == 2:
        return true
    if n % 2 == 0:
        return false
    
    let i = 3
    while i * i <= n:
        if n % i == 0:
            return false
        i += 2
    
    return true

# Function finding primes in a range
def find_primes(start: int, end: int):
    let primes = []
    let current = start
    
    while current <= end:
        if is_prime(current):
            primes.append(current)
        current += 1
    
    return primes

# Statistical analysis function
def analyze_numbers(numbers):
    let sum = 0
    let count = 0
    let min_val = numbers[0]
    let max_val = numbers[0]
    
    for n in numbers:
        sum += n
        count += 1
        
        if n < min_val:
            min_val = n
        if n > max_val:
            max_val = n
    
    let average = sum / count
    
    return {
        "sum": sum,
        "count": count,
        "average": average,
        "min": min_val,
        "max": max_val
    }

# Main execution
def main():
    print("=== Prime Number Finder ===")
    let primes = find_primes(1, 50)
    print("Primes from 1 to 50:")
    
    for p in primes:
        print(str(p) + " ", end="")
    print("")
    
    print("\n=== Statistical Analysis ===")
    let stats = analyze_numbers(primes)
    print("Count: " + str(stats["count"]))
    print("Sum: " + str(stats["sum"]))
    print("Average: " + str(stats["average"]))
    print("Min: " + str(stats["min"]))
    print("Max: " + str(stats["max"]))

# Entry point
main()
