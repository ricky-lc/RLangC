# RLangC Architecture Design

## Overview

RLangC implements a multi-stage compilation pipeline that supports both interpretation and native compilation from a shared intermediate representation.

## Design Principles

### 1. Separation of Concerns
Each compilation stage has a single, well-defined responsibility:
- **Lexer**: Text → Tokens
- **Parser**: Tokens → AST
- **Semantic Analyzer**: AST → Validated AST + Type Information
- **IR Generator**: AST → Intermediate Representation
- **Backends**: IR → Executable Code

### 2. Gradual Typing
- Default to dynamic types for rapid development
- Allow optional static type annotations
- Perform type inference where possible
- Enable mixing of static and dynamic code

### 3. Dual Execution Modes
- **Interpreter**: Direct execution from IR
  - Fast startup time
  - Interactive development
  - Debugging support
- **Native Compiler**: C code generation
  - Maximum performance
  - Standalone executables
  - Production deployments

## Pipeline Stages

### Stage 1: Lexical Analysis

**Input**: Source code text  
**Output**: Token stream

**Responsibilities**:
- Recognize keywords, identifiers, literals, operators
- Handle indentation-based and brace-based scoping
- Track source locations for error reporting
- Skip comments and whitespace

**Key Design Decisions**:
- Support both Python-style indentation and C-style braces
- Use INDENT/DEDENT tokens for indentation tracking
- Single-pass scanning for efficiency

### Stage 2: Syntax Analysis

**Input**: Token stream  
**Output**: Abstract Syntax Tree (AST)

**Responsibilities**:
- Build hierarchical program structure
- Validate syntax rules
- Preserve source locations
- Support both syntax styles

**Key Design Decisions**:
- Recursive descent parser for clarity
- Operator precedence climbing for expressions
- Support for optional type annotations
- Error recovery for better diagnostics

### Stage 3: Semantic Analysis

**Input**: AST  
**Output**: Validated AST + Symbol Table + Type Information

**Responsibilities**:
- Build symbol tables
- Perform type checking
- Infer types where not specified
- Validate semantic rules (e.g., const reassignment)

**Key Design Decisions**:
- Gradual typing: mix static and dynamic
- Type inference for unann otated variables
- Scope-based symbol resolution
- Compatible type checking with coercion rules

### Stage 4: IR Generation

**Input**: Validated AST  
**Output**: Intermediate Representation

**Responsibilities**:
- Generate platform-independent intermediate code
- Normalize control flow
- Prepare for backend consumption

**Key Design Decisions**:
- Stack-based IR for simplicity
- SSA form for optimization opportunities
- Control flow graph representation
- Platform-independent design

### Stage 5: Backend Execution

#### Interpreter Backend

**Input**: IR  
**Output**: Program execution

**Responsibilities**:
- Direct execution of IR instructions
- Runtime type checking
- Memory management
- Standard library integration

**Key Design Decisions**:
- Stack-based VM
- Reference counting + cycle detection
- Incremental garbage collection
- JIT compilation opportunities

#### Native Compilation Backend

**Input**: IR  
**Output**: C source code → Native executable

**Responsibilities**:
- Generate readable C code from IR
- Interface with system C compiler
- Optimize for target platform

**Key Design Decisions**:
- Generate ANSI C for portability
- Leverage C compiler optimizations
- Support multiple backends (C, Zig, Rust, LLVM)

## Runtime System

### Memory Management

**Strategy**: Incremental, Generational, Precise GC

**Components**:
1. **Allocator**: Fast bump allocation in young generation
2. **Collector**: Incremental mark-and-sweep
3. **Generations**: Young (frequent) and Old (infrequent)
4. **Precision**: Accurate pointer identification

**Key Design Decisions**:
- Young generation for short-lived objects
- Old generation promotion for survivors
- Incremental collection to reduce pauses
- Write barriers for generational collection

### Concurrency Support

**Model**: Async/await with event loop

**Components**:
1. **Event Loop**: Single-threaded execution
2. **Coroutines**: Suspendable functions
3. **Futures**: Asynchronous results
4. **Scheduler**: Fair task scheduling

**Key Design Decisions**:
- Cooperative multitasking
- Non-blocking I/O
- Message passing for isolation
- No shared mutable state

## Type System

### Type Hierarchy

```
any (top type)
├── int
├── float
├── str
├── bool
├── none
├── list[T]
├── dict[K, V]
├── function
└── class
```

### Type Rules

1. **Subtyping**: int <: float for numeric operations
2. **Inference**: Unify types from usage
3. **Compatibility**: Check at boundaries
4. **Coercion**: Implicit int → float

### Gradual Typing

- `any` type represents unknown/dynamic
- Static types checked at compile time
- Dynamic types checked at runtime
- Seamless mixing of static and dynamic

## Error Handling

### Compile-Time Errors

1. **Syntax Errors**: Invalid token sequences
2. **Type Errors**: Incompatible types
3. **Semantic Errors**: Undefined variables, const reassignment

### Runtime Errors

1. **Type Errors**: Dynamic type mismatches
2. **Null Errors**: Accessing none values
3. **Index Errors**: Out of bounds access
4. **Stack Overflow**: Deep recursion

## Optimization Strategies

### Compiler Optimizations

1. **Constant Folding**: Evaluate constant expressions
2. **Dead Code Elimination**: Remove unreachable code
3. **Inline Expansion**: Inline small functions
4. **Tail Call Optimization**: Optimize recursive calls

### Runtime Optimizations

1. **Inline Caching**: Cache method lookups
2. **Hidden Classes**: Optimize object layout
3. **JIT Compilation**: Compile hot paths
4. **Speculative Optimization**: Assume types, guard

## Testing Strategy

### Unit Tests
- Test each pipeline stage independently
- Verify correctness of transformations
- Check error handling

### Integration Tests
- Test complete pipeline
- Verify end-to-end behavior
- Test both execution modes

### Example Programs
- Demonstrate language features
- Serve as acceptance tests
- Document best practices

## Future Enhancements

1. **Pattern Matching**: Structural decomposition
2. **Traits/Interfaces**: Abstract types
3. **Modules**: Namespace management
4. **Macros**: Compile-time code generation
5. **LLVM Backend**: Direct IR generation
6. **Rust Backend**: Memory-safe code generation
7. **Zig Backend**: Simple, fast compilation

## References

- **Gradual Typing**: Siek & Taha (2006)
- **GC Design**: Jones & Lins (1996)
- **Compiler Design**: Appel (1998)
- **Type Inference**: Pierce (2002)
