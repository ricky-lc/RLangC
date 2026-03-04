# RLangC - A Modern Multi-Paradigm Language

RLangC is a general-purpose programming language that combines the best aspects of Python, JavaScript, and C to create a powerful, readable, and performant language.
Native compilation targets ~2.5x Python performance, and the language embraces braces, `let`/`const`, and low-level control so it does not feel solely Python-like.

## Design Philosophy

**Correctness First**: Static analysis and optional typing help catch errors before runtime.

**Clarity Matters**: Code should be easy to read and understand. Syntax choices prioritize human comprehension.

**Performance When Needed**: Dual execution modes target ~2.5x Python performance in native compilation while keeping fast interpreter iteration.

## Key Features

### 🎯 Gradual Typing
Start with dynamic types during prototyping, add static types as code matures:
```python
let x = 42                    # Dynamic
let y: int = 100              # Static
const PI: float = 3.14159     # Static constant
```

### 🔧 Flexible Syntax
Choose indentation (Python-style) or braces (C-style) based on preference:
```python
def greet(name):              # Indentation
    return "Hello, " + name

def greet(name) {             # Braces
    return "Hello, " + name
}
```

### ⚡ Dual Execution
- **Interpreter**: Fast iteration, interactive development
- **Native Compiler**: Production-ready performance via C backend

### 🚀 Modern Features
- First-class functions
- List comprehensions
- Pattern matching (planned)
- Concurrent execution primitives
- Incremental, generational GC

## Quick Start

### Installation (Developer Bootstrap)
```bash
pip install rlangc
```

### Hello World
```python
def main():
    print("Hello, RLangC!")

main()
```

### Running Code
```bash
# Compile to a native executable (C toolchain required)
rlangc compile program.rl -o program
./program
```

The current implementation path is native-first: `rlangc compile` emits C and builds a standalone executable, so execution is not tied to `pip` at runtime.

## Language Tour

### Variables and Constants
```python
# Mutable variables
let counter = 0
counter += 1

# Immutable constants
const MAX_USERS = 1000
```

### Functions
```python
# Simple function
def square(x):
    return x * x

# With types
def divide(a: float, b: float) -> float:
    return a / b

# Default arguments
def greet(name, greeting="Hello"):
    return greeting + ", " + name
```

### Control Flow
```python
# Conditionals
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# Loops
while condition:
    do_something()

for item in collection:
    process(item)
```

### Data Structures
```python
# Lists
numbers = [1, 2, 3, 4, 5]
first = numbers[0]

# Iteration
for n in numbers:
    print(n)
```

## Architecture

```
┌─────────────────┐
│  Source Code    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Lexer   │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Parser  │
    └────┬─────┘
         │
  ┌──────▼──────┐
  │  Semantic   │
  │  Analysis   │
  └──────┬──────┘
         │
    ┌────▼─────┐
    │    IR    │
    └────┬─────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Inter- │ │ Native  │
│preter │ │Backend  │
└───────┘ └──┬──────┘
             │
          ┌──▼──────┐
          │C Compiler│
          └──┬──────┘
             │
        ┌────▼─────┐
        │Executable│
        └──────────┘
```

## Compilation Pipeline

1. **Lexer**: Converts source text into tokens
2. **Parser**: Builds abstract syntax tree (AST)
3. **Semantic Analysis**: Type checking and validation
4. **IR Generation**: Creates intermediate representation
5. **Backend**: Either interprets IR or generates C code

## Runtime System

### Memory Management
- **Generational GC**: Young and old generations
- **Incremental Collection**: Reduces pause times
- **Precise Tracking**: Accurate pointer identification

### Concurrency (Planned)
- Async/await syntax
- Green threads
- Message passing
- Lock-free data structures

## Project Structure

```
RLangC/
├── spec/           # Language specification
├── examples/       # Example programs
├── docs/           # Documentation
├── src/            # Implementation (to be added)
└── tests/          # Test suite (to be added)
```

## Examples

See the `examples/` directory for complete programs demonstrating:
- Basic syntax and features
- Type system usage
- Function definitions
- Control flow patterns
- Data structure manipulation

## Development Status

RLangC is in active design and development. The language specification is complete, and implementation is progressing incrementally with focus on:

1. ✅ Core language design
2. ✅ Specification documentation
3. 🚧 Lexer and parser implementation
4. 🚧 Type system and semantic analysis
5. 📋 Bytecode interpreter
6. 📋 C code generation backend
7. 📋 Runtime library
8. 📋 Standard library

## Contributing

The language design welcomes feedback and suggestions. See CONTRIBUTING.md for details.

## License

[To be determined]

## Contact

[Project details to be added]

---

*"Clarity, correctness, performance - in that order."*
