# RLangC Language Specification

## Overview

RLangC is a general-purpose programming language designed to blend:
- **Python's readability**: Clean syntax with indentation-based scoping
- **JavaScript's expressiveness**: Flexible and dynamic features
- **C's familiarity**: Recognizable control structures and operators
It also embraces braces, `let`/`const` bindings, and low-level controls so the overall feel is not purely Python-like.

## Core Priorities

1. **Correctness**: Static analysis and optional type checking catch errors early
2. **Clarity**: Readable syntax that expresses intent clearly
3. **Performance**: Dual execution modes with a native target of ~2.5x Python performance

## Semantics

- **Lexical scoping**: Blocks (indentation or braces) create scopes; inner bindings shadow outer ones.
- **Bindings**: `let` introduces mutable bindings, `const` introduces immutable bindings.
- **Evaluation order**: Expressions and call arguments evaluate left-to-right before the call executes.
- **Value vs reference**: Primitive values are copied; collections and objects are reference types.
- **`none`**: Represents the absence of a value and is the only null-like sentinel.
- **Modules**: Top-level statements execute in order; imports bind module namespaces.
- **Property access**: `obj.name` is syntactic sugar for `obj["name"]`.

## Language Features

### Gradual Typing

RLangC supports gradual typing with dynamic defaults and optional static types with inference:

- Static annotations enable specialization in IR, removing dynamic checks and unlocking native-code optimizations.
- Annotations can appear per variable, per function signature, or at module scope (`@typed`) to opt into stricter checking.

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

Functions use the `def` keyword. **Note**: Arrow function syntax is intentionally not supported to keep multi-line functions explicit and Python-like.

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

### Objects and Dictionaries

Objects are dictionary-like structures with string keys:

```python
let user = {"name": "Ada", "age": 36}
print(user["name"])
user["role"] = "engineer"
```

Property access is supported as syntactic sugar for string keys:

```python
print(user.name)  # Equivalent to user["name"]
```

`object` is a specialized, string-keyed record type with shape optimization; `dict` remains the general key/value map.
Use `object` for record-like data with stable string keys, and `dict` for arbitrary keys or highly dynamic shapes.
Using `dict` with non-string keys uses hash tables and skips shape optimization, while `object` keeps inline slots for faster property access.

### Modules and Imports

```python
import math
import net.http as http

let radius = 4.0
let area = math.pi * radius * radius
```

### Error Handling

RLangC uses **exceptions** for ergonomics and consistency with Python/JS. Exceptions can unwind control flow, while `defer` ensures deterministic cleanup for external resources.

```python
def read_config(path):
    try:
        let text = io.read_file(path)
        return parse_config(text)
    except IOError as err:
        log.error("Failed to read config: " + err.message)
        return none
    finally:
        cleanup()
```

### Foreign Function Interface (FFI)

```python
extern "C" def c_sin(x: float) -> float
extern "Rust" def hash_bytes(data: list) -> int

let value = c_sin(1.57)
```

## Execution Modes

### Interpreter Mode

Direct execution through bytecode interpreter:
- Fast startup
- Interactive REPL
- Ideal for development and scripting

### Native Compilation Mode

Compilation to native code is planned via an initial C backend, with future support for Zig, Rust, and direct LLVM IR emission:
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

Built-in support for concurrent programming with an event-loop scheduler that cooperates with the GC:
```python
# Conceptual syntax (to be implemented)
async def fetch_data(url):
    return await http_get(url)
```

### Memory Management

- **Generational**: Young/old spaces with fast promotion
- **Incremental + concurrent**: Collector runs alongside application code (mutator) to reduce pauses
- **Precise + compacting**: Exact pointer maps with compaction to limit fragmentation
- **Write barriers**: Maintain remembered sets for generational and concurrent safety
- **Bump-pointer allocation**: Fast allocation in the young generation

## Type System

### Built-in Types

- `int`: Integer numbers
- `float`: Floating-point numbers
- `str`: Text strings
- `bool`: Boolean values (true/false)
- `none`: Null/absence of value
- `list`: Ordered collections
- `dict`: Key/value collections
- `set`: Unique-value collections
- `object`: String-keyed dict with shape metadata
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

## Standard Library Outline

- **core**: `print`, `len`, `type`, `assert`, `defer`, `range`, `format`
- **collections**: lists, dicts, sets, iterators, sorting
- **io**: files, streams, paths, serialization, `IOError` exceptions
- **net**: HTTP, sockets, DNS
- **concurrency**: tasks, futures, channels, locks
- **time**: timers, clocks, scheduling
- **ffi**: C/Rust/Zig bindings

## Example Programs

See the `examples/` directory for complete program demonstrations, including:
- Hello world and control flow
- Typed vs untyped variables and functions
- Objects/dictionaries and collections
- Async/await usage
- Native compilation workflow

## Implementation Status

This specification documents the language design. Core features are being implemented progressively, focusing on correctness and clarity before performance optimization.
