def addition(a, b):
    return a + b


def subtraction(a, b):
    return a - b


def multiplication(a, b):
    return a * b


def division(a, b):
    return a / b


def selection(operation, a, b):
    if operation == 1:
        return addition(a, b)
    elif operation == 2:
        return subtraction(a, b)
    elif operation == 3:
        return multiplication(a, b)
    else:
        return division(a, b)


print("Please select operation -\n "
      "1. Add\n "
      "2. Subtract\n"
      "3. Multiply\n"
      "4. Divide\n")

# Take input from the user
select = int(input("Select operations form 1, 2, 3, 4 :"))
number_1 = int(input("Enter first number: "))
number_2 = int(input("Enter second number: "))


print(selection(select, number_1, number_2))
