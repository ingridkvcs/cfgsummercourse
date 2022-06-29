"""
Write a function that will accept an array of numbers and an integer representing a target sum

If any two numbers from the accepted numbers sum up to the target sum, then your function should
return them in an array, in any order.

If no two numbers sum up to the target sum, the function should return an empty array.

Note that the target sum has to be obtained by summing two different numbers in the array,
you cannot add a single integer to itself in order to obtain the target sum.

"""


def find_pair(my_list, num):
    if my_list is None or num is None:
        raise TypeError("No value passed to the parameters")
    for i in range(len(my_list)):
        for j in range(len(my_list)):
            if i != j:
                sum_pair = my_list[i] + my_list[j]
                if sum_pair == num:
                    return my_list[i], my_list[j]

    return []


if __name__ == '__main__':
    my_numbers = [3, 5, -4 ,8, 11, 1, -1, 6]
    target_sum = 10

    print(find_pair(my_numbers, target_sum))
