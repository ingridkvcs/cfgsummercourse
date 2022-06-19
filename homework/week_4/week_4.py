# Question 1

"""
Simple ATM program
Using exception handling code blocks such as try/ except / else / finally, write a program that simulates an ATM machine to withdraw money.
(NB: the more code blocks the better, but try to use at least two key words e.g. try/except)
Tasks:
1.       Prompt user for a pin code
2.       If the pin code is correct then proceed to the next step, otherwise ask a user to type in a password again. You can give a user a maximum of 3 attempts and then exit a program.
3.       Set account balance to 100.
4.       Now we need to simulate cash withdrawal
5.       Accept the withdrawal amount
6.       Subtract the amount from the account balance and display the remaining balance (NOTE! The balance cannot be negative!)
7.       However, when a user asks to ‘withdraw’ more money than they have on their account, then you need to raise an error an exit the program.

"""

account_balance = 100
correct_pin = 2846
valid_pin = False

for attempt in range(3):
    user_pin_code = input("Enter your PIN: ")
    try:
        if not user_pin_code:
            raise Exception("Please enter a PIN.")
        if int(user_pin_code) != correct_pin:
            raise Exception("PIN incorrect.")
    except Exception as ex:
        print(ex)
    else:
        valid_pin = True
        break

if not valid_pin:
    raise Exception("Invalid PIN 3 times - unauthorised, so exiting")

requested_sum = 0
while not requested_sum:
    requested_sum = input("Introduced the sum you want to withdraw: ")

if int(requested_sum) < 0:
    raise Exception("Cannot input negative numbers")

if int(requested_sum) > account_balance:
    raise Exception("Insufficient funds. Try different amount.")

account_balance -= int(requested_sum)
print(account_balance)

# from random import randint
#
# def test_try():
#     try:
#         x = randint(0, 100)
#         if x < 20:
#             raise Exception("Number too low")
#         if x < 50:
#             raise Exception("Halfy")
#         x = x * 3
#         print("Yas man " + str(x))
#     finally:
#         print("Oh well, at least it's done")
#
#     print("AFTER")
#
# try:
#     test_try()
# except Exception as ex:
#     print("close one: " + str(ex))
