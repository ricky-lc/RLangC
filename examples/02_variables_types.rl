# Variables and Type System Examples (Typed vs Untyped)

# Dynamic typing (default)
let message = "Welcome to RLangC"
let count = 42
let ratio = 3.14

print(message)
print(count)
print(ratio)

# Static typing with annotations
let name: str = "Alice"
let age: int = 30
let height: float = 5.8

print(name + " is " + str(age) + " years old")

# Constants (immutable)
const MAX_ATTEMPTS = 3
const API_KEY = "secret-key-12345"
const RATE_LIMIT: int = 100

print("Max attempts: " + str(MAX_ATTEMPTS))

# Type inference
const PI = 3.14159  # Inferred as float
let counter = 0     # Inferred as int
let flag = true     # Inferred as bool

# Compound assignment operators
counter += 1
counter *= 2
print("Counter: " + str(counter))
