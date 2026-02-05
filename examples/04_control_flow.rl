# Control Flow Examples

# If-elif-else statements
def check_temperature(temp: int) -> str:
    if temp > 30:
        return "Hot"
    elif temp > 20:
        return "Warm"
    elif temp > 10:
        return "Cool"
    else:
        return "Cold"

print(check_temperature(35))
print(check_temperature(25))
print(check_temperature(15))
print(check_temperature(5))

# While loops
def count_down(n: int):
    while n > 0:
        print(str(n))
        n -= 1
    print("Blast off!")

count_down(5)

# For-in loops with lists
def sum_list(numbers):
    let total = 0
    for num in numbers:
        total += num
    return total

let my_numbers = [1, 2, 3, 4, 5]
print("Sum: " + str(sum_list(my_numbers)))

# Nested loops example
def multiplication_table(n: int):
    let i = 1
    while i <= n:
        let j = 1
        while j <= n:
            print(str(i * j) + " ", end="")
            j += 1
        print("")  # New line
        i += 1

multiplication_table(5)

# Break and continue (conceptual)
def find_first_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            return num
    return none

print("First even: " + str(find_first_even([1, 3, 5, 6, 7])))
