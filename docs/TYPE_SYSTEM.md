# RLangC Type System

## Philosophy

RLangC implements **gradual typing**, which allows developers to start with dynamic types during prototyping and progressively add static type annotations as code matures.

## Core Principles

1. **Dynamic by Default**: Variables without type annotations are dynamically typed
2. **Optional Static Types**: Add type annotations for safety and documentation
3. **Type Inference**: Compiler infers types from context when possible
4. **Compatibility**: Static and dynamic code can coexist seamlessly

## Built-in Types

### Primitive Types

#### `int` - Integer Numbers
```python
let count: int = 42
let negative: int = -100
```

#### `float` - Floating Point Numbers
```python
let pi: float = 3.14159
let ratio: float = 0.5
```

#### `str` - Text Strings
```python
let message: str = "Hello, World!"
let empty: str = ""
```

#### `bool` - Boolean Values
```python
let flag: bool = true
let condition: bool = false
```

#### `none` - Null/Absence
```python
let value: none = none
```

### Collection Types

#### `list` - Ordered Collections
```python
let numbers: list = [1, 2, 3, 4, 5]
let names: list = ["Alice", "Bob", "Charlie"]
let mixed: list = [1, "two", 3.0]  # Heterogeneous allowed
```

### Special Types

#### `any` - Dynamic Type
The default type for unannotated variables. Represents any possible value.

```python
let dynamic = 42  # Type: any
dynamic = "text"  # OK - any accepts any type
```

## Type Annotations

### Variable Annotations

```python
# With type
let age: int = 30

# Without type (inferred as any or from initializer)
let name = "Alice"  # Inferred from "Alice"

# Constant with type
const MAX: int = 100
```

### Function Annotations

```python
# Parameter and return types
def add(x: int, y: int) -> int:
    return x + y

# Only return type
def greet(name) -> str:
    return "Hello, " + name

# No annotations (all any)
def process(data):
    return data * 2
```

## Type Inference

The compiler infers types in several contexts:

### From Literals
```python
let x = 42        # Inferred: int
let y = 3.14      # Inferred: float
let z = "text"    # Inferred: str
let flag = true   # Inferred: bool
```

### From Operations
```python
let a = 10
let b = 20
let sum = a + b   # Inferred: int

let x = 3.14
let y = 2.0
let product = x * y  # Inferred: float
```

### From Function Returns
```python
def get_count() -> int:
    return 42

let value = get_count()  # Inferred: int
```

## Type Checking Rules

### Assignment Compatibility

```python
# OK: Same type
let x: int = 42
let y: int = x

# OK: Subtype (int to float)
let a: int = 10
let b: float = a  # Implicit conversion

# Error: Incompatible types
let s: str = 42  # Type error
```

### Function Call Compatibility

```python
def greet(name: str) -> str:
    return "Hello, " + name

greet("Alice")  # OK
greet(42)       # Type error
```

### Const Immutability

```python
const PI = 3.14159
PI = 3.14  # Error: cannot reassign constant
```

## Type Coercion

### Numeric Widening

```python
let i: int = 42
let f: float = i  # OK: int → float (widening)

let f2: float = 3.14
let i2: int = f2  # Error: float → int requires explicit cast
```

### String Concatenation

```python
let s = "Count: " + str(42)  # Explicit conversion required
```

## Gradual Typing in Practice

### Starting Dynamic

```python
# Initial prototype - all dynamic
def process_data(data):
    let result = []
    for item in data:
        result.append(item * 2)
    return result
```

### Adding Types Progressively

```python
# Add input type
def process_data(data: list):
    let result = []
    for item in data:
        result.append(item * 2)
    return result
```

### Fully Typed

```python
# Complete type annotations
def process_data(data: list) -> list:
    let result: list = []
    for item in data:
        result.append(item * 2)
    return result
```

## Type System Features

### Structural Typing (Future)

Types are compatible if their structure matches:

```python
# Both have same structure
let point1 = {x: 10, y: 20}
let point2 = {x: 5, y: 15}

def distance(p1, p2):
    let dx = p1.x - p2.x
    let dy = p1.y - p2.y
    return sqrt(dx * dx + dy * dy)
```

### Generic Types (Future)

```python
def identity<T>(x: T) -> T:
    return x

let num: int = identity<int>(42)
let text: str = identity<str>("hello")
```

### Union Types (Future)

```python
def parse(input: str | int) -> int:
    if typeof(input) == str:
        return int(input)
    return input
```

### Optional Types (Future)

```python
def find(items: list, target) -> int?:
    for i, item in enumerate(items):
        if item == target:
            return i
    return none  # Returns optional int
```

## Type Errors

### Compile-Time Errors

Detected when static types are used:

```python
let x: int = "text"  # Error: cannot assign str to int

def add(a: int, b: int) -> int:
    return a + b

add("1", "2")  # Error: expected int, got str
```

### Runtime Errors

Detected when dynamic types are used incorrectly:

```python
let x = "text"
let y = x + 5  # Runtime error: cannot add str and int
```

## Best Practices

1. **Start Dynamic**: Use untyped variables during prototyping
2. **Add Types at Boundaries**: Type function parameters and returns
3. **Use Inference**: Let compiler infer obvious types
4. **Type Public APIs**: Always type public-facing code
5. **Mix Strategically**: Use dynamic types for flexible code, static for critical paths

## Examples

### Dynamic Example

```python
def process(data):
    let results = []
    for item in data:
        if item > 0:
            results.append(item * 2)
    return results
```

### Static Example

```python
def process(data: list) -> list:
    let results: list = []
    let item: int
    for item in data:
        if item > 0:
            results.append(item * 2)
    return results
```

### Mixed Example

```python
# Public API is typed
def calculate_average(numbers: list) -> float:
    # Internal implementation uses inference
    let sum = 0
    let count = 0
    
    for num in numbers:
        sum += num
        count += 1
    
    return sum / count
```

## Future Enhancements

1. **Dependent Types**: Types that depend on values
2. **Refinement Types**: Types with predicates
3. **Effect Types**: Track side effects in types
4. **Linear Types**: Resource management via types
5. **Type Classes**: Ad-hoc polymorphism
