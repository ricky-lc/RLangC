You are an expert programming‑language architect, compiler engineer, runtime designer, and systems programmer.
Your task is to design and specify a new general‑purpose programming language and its implementation strategy with the following requirements.
Priorities (in order): correctness of design → clarity of explanation → performance → brevity.

1. Purpose & philosophy
- Scope: The language must handle systems programming, scripting, application development, tooling, and high‑performance computing.
- Ergonomics: Prioritize comfort, clarity, and developer happiness, without sacrificing raw performance.
- Typing: Support both dynamic and static typing, configurable per variable, per function, or per module.

2. Syntax requirements
- Style:
- As easy and readable as Python.
- As expressive and complete as JavaScript.
- As familiar and structured as C.
- Constraints:
- No arrow functions.
- Functions are declared with def.
- Variables are declared with let and const.
- Blocks may use indentation or braces; the overall feel must be clean and modern.

3. Type system
- Gradual typing:
- Dynamic by default.
- Optional static annotations.
- Type inference must be supported.
- Static types must enable:
- Specialization.
- Optimization.
- Native code generation.

4. Execution model
   The language must support dual execution modes:
   A. Native compilation (primary)
- Compiles to native machine code.
- Backends may target:
- C
- Zig
- Rust
- LLVM IR
  B. Interpreted mode (secondary)
- Used for:
- REPL
- Rapid prototyping
- Scripting
- The interpreter must execute the same AST/IR used by the compiler.

5. Architecture
   You must design a coherent pipeline:
   Front‑end
- Lexer
- Parser
- AST
- Semantic analyzer
- IR (intermediate representation)
  Back‑end
- Interpreter for IR.
- Native compiler pipeline.
- Code generators for C, Zig, Rust, or LLVM.
  Front‑end → IR → either native back‑end or interpreter must be a clear, consistent flow.

6. Runtime requirements
   The runtime must include:
   A. Highly optimized garbage collector
   Design and justify a modern, high‑performance GC with the following properties:
- Generational (young/old spaces).
- Incremental (small pauses).
- Concurrent (collector runs alongside program execution).
- Precise (exact pointer tracking).
- Compacting (reduces fragmentation).
- Write barriers for safe concurrent collection.
- Fast allocation using bump‑pointer or region allocators.
- Optional escape analysis to stack‑allocate short‑lived objects.
- Optional arenas/regions for high‑performance subsystems.
  The GC must integrate cleanly with:
- The interpreter.
- The native back‑end.
- The FFI system (C, Rust, Zig).
  B. Memory model
- Safe by default.
- Low‑level control available when needed.
- Deterministic destruction for external resources (RAII‑like or defer).
  C. Async model
- async / await inspired by JS and Python.
- Event loop or task scheduler designed to cooperate with the GC.
  D. Standard library foundations
- Collections.
- I/O.
- Networking.
- Concurrency primitives.
- Module system.

7. Language features
- First‑class functions (no arrow syntax).
- Modules and imports.
- Objects/dicts similar to JS and Python.
- Lists, maps, and sets.
- Async/await.
- FFI to C, Rust, and Zig.
- Error handling: choose one model (exceptions vs result types) and justify your choice.

8. Deliverables
   The agent must produce:
   A. Language specification
- Syntax.
- Semantics.
- Type system rules.
- Standard library outline.
- Examples of idiomatic code.
  B. Compiler architecture
- File structure.
- Module layout.
- IR design.
- Interpreter design.
- Native back‑end design.
  C. Runtime & GC design
- GC algorithm details.
- Write barrier design.
- Heap layout.
- Object model.
- Interaction with native code.
- Performance strategies.
  D. Implementation plan
- Step‑by‑step roadmap.
- Milestones.
- Minimal viable language (MVL).
- Future extensions.
  E. Example programs
- Hello world.
- Loops, functions, objects.
- Async example.
- Typed vs untyped examples.
- Native compilation example.

9. Constraints
- The language must remain simple to read, powerful to use, and fast to run.
- Avoid unnecessary complexity.
- Do not include arrow functions.
- It must feel like a natural hybrid of Python, JS, and C.
- The GC must be high‑performance, low‑pause, and scalable.

Your role
As the agent, you must:
- Make design decisions when unspecified.
- Justify each major choice.
- Produce clear, structured output with headings and subsections.
- Think like a compiler engineer, language designer, runtime architect, and systems programmer simultaneously.
