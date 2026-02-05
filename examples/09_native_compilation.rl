# Native Compilation Example
# Compile: rlangc compile examples/09_native_compilation.rl -o native_example
# Run: ./native_example

def fib(n: int) -> int:
    let previous = 0
    let current = 1
    for _ in range(n):
        let temp = current
        current = previous + current
        previous = temp
    return previous

def main():
    let value = fib(10)
    print(format("fib(10) = {}", value))

main()
