# Data Structures - Lists and Collections

# Creating lists
let numbers = [1, 2, 3, 4, 5]
let names = ["Alice", "Bob", "Charlie"]
let mixed = [1, "two", 3.0, true]

print("Numbers: " + str(numbers))
print("Names: " + str(names))

# Accessing elements
let first_number = numbers[0]
let last_name = names[2]

print("First number: " + str(first_number))
print("Last name: " + last_name)

# Iterating over lists
print("Iterating numbers:")
for n in numbers:
    print(str(n))

print("Iterating names:")
for name in names:
    print(name)

# List operations
def find_max(nums):
    let max_val = nums[0]
    for n in nums:
        if n > max_val:
            max_val = n
    return max_val

let values = [3, 7, 2, 9, 1, 5]
print("Max value: " + str(find_max(values)))

# List filtering
def filter_positive(nums):
    let result = []
    for n in nums:
        if n > 0:
            result.append(n)
    return result

let test_nums = [-2, 5, -8, 3, 0, 7]
let positive_nums = filter_positive(test_nums)
print("Positive numbers: " + str(positive_nums))

# List transformation
def double_all(nums):
    let result = []
    for n in nums:
        result.append(n * 2)
    return result

let doubled = double_all([1, 2, 3, 4])
print("Doubled: " + str(doubled))
