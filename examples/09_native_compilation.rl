# Native Compilation Example
# Compile: rlangc compile examples/09_native_compilation.rl -o native_example
# Run: ./native_example

def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

def main():
    let value = fib(10)
    print("fib(10) = " + str(value))

main()
