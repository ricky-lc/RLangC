# RLangC Language Specification

## Overview

RLangC is a general-purpose programming language designed to blend:
- **Python's readability**: Clean syntax with indentation-based scoping
- **JavaScript's expressiveness**: Flexible and dynamic features
- **C's familiarity**: Recognizable control structures and operators

## Core Priorities

1. **Correctness**: Static analysis and optional type checking catch errors early
2. **Clarity**: Readable syntax that expresses intent clearly
3. **Performance**: Dual execution modes for different use cases

## Language Features

### Gradual Typing

RLangC supports gradual typing with dynamic defaults and optional static types with inference:

```python
# Dynamic typing (default)
let x = 42
let message = "hello"

# Optional static typing
let count: int = 0
let ratio: float = 3.14
let name: str = "Alice"

# Type inference from initializer
const PI = 3.14159  # Inferred as float
```

### Function Definitions

Functions use the `def` keyword:

```python
# Simple function
def greet(name):
    return "Hello, " + name

# With type annotations
def add(x: int, y: int) -> int:
    return x + y

# With default parameters
def power(base: float, exponent: float = 2.0) -> float:
    return base ** exponent
```

### Variable Declarations

Two declaration keywords:
- `let`: Mutable variable
- `const`: Immutable constant

```python
let counter = 0
counter = counter + 1  # OK

const MAX_SIZE = 100
MAX_SIZE = 200  # Error: cannot reassign constant
```

### Dual Syntax Support

Both indentation and braces are supported:

```python
# Indentation style (Python-like)
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

# Brace style (C-like)
def factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
```

### Control Flow

```python
# If-elif-else
if temperature > 30:
    print("Hot")
elif temperature > 20:
    print("Warm")
else:
    print("Cold")

# While loop
let i = 0
while i < 10:
    print(i)
    i = i + 1

# For-in loop
for item in collection:
    process(item)
```

### Operators

Full set of operators:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**` (power), `//` (floor division)
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical: `and`, `or`, `not`
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`

### Collections

```python
# Lists
let numbers = [1, 2, 3, 4, 5]
let first = numbers[0]

# List iteration
for num in numbers:
    print(num)
```

## Execution Modes

### Interpreter Mode

Direct execution through bytecode interpreter:
- Fast startup
- Interactive REPL
- Ideal for development and scripting

### Native Compilation Mode

Compilation to native code via C backend:
- Maximum performance
- Standalone executables
- Production deployments

Both modes share a common intermediate representation (IR).

## Compilation Pipeline

```
Source Code
    ↓
Lexer (Tokenization)
    ↓
Parser (AST Construction)
    ↓
Semantic Analysis (Type Checking)
    ↓
IR Generation
    ↓
    ├─→ Interpreter (Direct Execution)
    └─→ C Backend → Native Code
```

## Runtime Features

### Concurrent Execution

Built-in support for concurrent programming:
```python
# Conceptual syntax (to be implemented)
async def fetch_data(url):
    return await http_get(url)
```

### Memory Management

- **Incremental**: Reduces pause times
- **Generational**: Optimizes for common patterns
- **Precise**: Accurate object tracking

## Type System

### Built-in Types

- `int`: Integer numbers
- `float`: Floating-point numbers
- `str`: Text strings
- `bool`: Boolean values (true/false)
- `none`: Null/absence of value
- `list`: Ordered collections
- `any`: Dynamic type (default)

### Type Inference

The compiler infers types when not explicitly specified:

```python
let x = 42          # Inferred: int
let y = 3.14        # Inferred: float
let z = x + y       # Inferred: float (widening)
```

### Type Compatibility

- Implicit numeric conversions (int → float)
- Structural typing for collections
- Gradual typing allows mixing static and dynamic code

## Example Programs

See the `examples/` directory for complete program demonstrations.

## Implementation Status

This specification documents the language design. Core features are being implemented progressively, focusing on correctness and clarity before performance optimization.
