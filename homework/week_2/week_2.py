# Task 3 -  Question 1

# chairs = '15'
# nails = 4
# total_nails = chairs * nails
# message = 'I need to buy {} nails'.format(total_nails)
# print(message)

# Correct code:

# chairs = 15
# nails = 4
# total_nails = chairs * nails
# message = 'I need to buy {} nails'.format(total_nails)
# print(message)
#
# # Task 2 -  Question 2

# my_name = 'Penelope'
# my_age = 29
# message = 'My name is {} and I am {} years old'.format(my_name, my_age)
# print(message)


# Task 2 - Question 3

# def calculate_omelettes(boxes, eggs_in_box, eggs_per_omelette):
#     return (boxes*eggs_in_box)/eggs_per_omelette
#
#
# egg_boxes = 6
#
# print("You can make " + str(calculate_omelettes(egg_boxes, 6, 4)) + " omelettes with " + str(egg_boxes) + " boxes of eggs.")


# Task 2 - Question 4

# Task 1 - Replace the (.) character with (!) instead.
# Output should be “I love coding!”

# my_str = "I love coding."
# my_str = my_str.replace(".", "!")
#
# print(my_str)

# Task 2 - Reassign str so that all of its characters are lowercase.

# my_str_1 = "EVERY Exercise Brings Me Closer to Completing my GOALS."
# my_str_1=my_str_1.lower()
#
# print(my_str_1)

# Task 3 - Output whether this string starts with an A or not
# my_str_2 = "We enjoy travelling"
# ans_1 = my_str_2.startswith('A')
# print(ans_1)

# Task4 - What is the length of the given string?

# my_str_3="1.458.001"
# ans_2= len(my_str_3)
# print(ans_2)

# Question 5

# Task 1 - Slice the word so that you get "thon".
# wrd="Python"
# ans_1= wrd[2:]
# print(ans_1)

# Task 2 - Slice the word until "o". (Pyth)
# wrd="Python"
# ans_1=wrd.find('o')
# ans_2=wrd[:ans_1]
# print(ans_2)

# Task 3 - Now try to get "th" only.
# wrd="Python"
# ans_1=wrd[2:4]
# print(ans_1)

# Task 4 - Now slice the word with steps of 2, excluding first and last characters
# wrd="Python"
# ans_1=wrd[1:-1:2]
# print(ans_1)

# Question 6
# for number in range(100):
#     output = 'o' * number
#     print(output)
# This block of code prints an increasing number of 'o' on each line starting from 0 up until 99 'o's, generating a triangle.

# Question 7

# def calculate_vat(amount):
#     return amount * 1.2
#
#
# total = calculate_vat(100)
# print(total)

# Question 8

# Write a new function to print a ‘cashier receipt’ output for a shop (any shop – clothes, food, events etc).
# It should accept 3 items, then sum them up and print out a detailed receipt with TOTAL

# def receipt(item1, item2, item3):
#     print(item1[0] + '\t' + str(item1[1]))
#     print(item2[0] + '\t' + str(item2[1]))
#     print(item3[0] + '\t' + str(item3[1]))
#
#     total = sum((item1[1], item2[1], item3[1]))
#     print("Total:\t" + str(total))
#
#
# receipt(("t-shirt", 12.99), ("dress", 24.99), ("jeans", 17.99))
