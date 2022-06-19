# Question 1

# rainy_day = input("Is it raining today? (y/n)")
# if rainy_day == "y":
# 	print("Take an umbrella!")
# else:
# 	print("No need for an umbrella!")

# Question 2

# my_money = input('How much money do you have? ')
# boat cost = 20 + 5
# if my_money < boat_cost:
# print('You can afford the boat hire')
# else :
# print('You cannot afford the board hire')

# Correct code

# my_money = input('How much money do you have? ')
# boat_cost = 20 + 5
# if int(my_money) < boat_cost:
# 	print('You cannot afford the boat hire')
# else :
# 	print('You can afford the board hire')

# Question 3


# def determine_century(year):
#     if year < 1800:
#         print("We don't keep book from before 1800")
#     elif year == 1800:
#         return "Eighteenth Century"
#     elif year <= 1900:
#         return "Nineteenth Century"
#     elif year <= 1950:
#         return "Twentieth Century"
#     else:
#         print("Too new for us!")
#
#
# def determine_decade(year):
#     decade = int((year % 100) / 10)
#     match decade:
#         case 0:
#             return "Hundreds"
#         case 1:
#             return "Tens"
#         case 2:
#             return "Twenties"
#         case 3:
#             return "Thirties"
#         case 4:
#             return "Forties"
#         case 5:
#             return "Fifties"
#         case 6:
#             return "Sixties"
#         case 7:
#             return "Seventies"
#         case 8:
#             return "Eighties"
#         case 9:
#             return "Nineties"
#
#
# input_year = int(input("Insert a year: "))
# if input_year < 1800 or input_year > 1950:
#     print("Year not in range")
# else:
#     print(determine_century(input_year) + ", " + determine_decade(input_year))

# Question 1

# shopping_list = [
# "oranges",
# "cat food",
# "sponge cake",
# "long-grain rice",
# "cheese board",
# ]
# print(shopping_list[0])


# Question 2

# chocolates = {
#     'white': 1.50,
#     'milk': 1.20,
#     'dark': 1.80,
#     'vegan': 2.00,
# }
# choc_choice = input("What chocolate do you want? ")
# print(chocolates[choc_choice])

# Question 3

# import random
#
# def get_random_lottery_numbers():
#     lottery_numbers = set()
#     for _ in range(7):
#         lottery_numbers.add(random.randint(0, 100))
#     return lottery_numbers
#
#
# lottery_tickets = {14, 67, 12, 91, 11, 34, 69}
#
# lottery_winner_numbers = get_random_lottery_numbers()
# lottery_winner_numbers = {11, 31, 69, 67, 7, 8, 23}
#
# matched_numbers = len(lottery_tickets.intersection(lottery_winner_numbers))
#
# match matched_numbers:
#     case 3:
#         prize = 20
#     case 4:
#         prize = 40
#     case 5:
#         prize = 100
#     case 6:
#         prize = 100000
#     case 7:
#         prize = 1000000
#     case _:
#         prize = 0
#
# print(f"Prize is £{prize}")



# Question 2 from Read and Write files
#
# This program should save my data to a file, but it doesn't work when I run  it.
# What is the problem and how do I fix it?
#
# poem = 'I like Python and I am not very good at poems'
# with open('poem.txt', 'w') as poem_file:
#         poem_file.write(poem)

# fixed it by changing it from read mode to write mode.

# Question 3

# from os.path import exists
#
# elton_john_lyrics = '''You could never know what it's like
# Your blood like winter freezes just like ice
# And there's a cold lonely light that shines from you You'll wind up like the wreck you hide behind that mask you use
# And did you think this fool could never win?
# Well look at me, I'm coming back again
# I got a taste of love in a simple way
# And if you need to know while I'm still standing, you just fade away
# Don't you know I'm still standing better than I ever did Looking like a true survivor, feeling like a little kid
# I'm still standing after all this time
# Picking up the pieces of my life without you on my mind
# I'm still standing (Yeah, yeah, yeah)
# I'm still standing (Yeah, yeah, yeah)
# '''
#
# lyrics_file_name = 'song_lyrics.txt'
#
# with open(lyrics_file_name, 'w') as lyrics_file:
#     lyrics_file.write(elton_john_lyrics)
#
#
# if exists(lyrics_file_name):
#     print("Lyrics have been saved to file.")
#
# with open(lyrics_file_name, 'r') as lyrics_file:
#     lyrics = lyrics_file.readlines()
#
# for lyric in lyrics:
#     if 'still' in lyric:
#         print(lyric)


# API
# Question 1
import requests

pokemon_ids = [12, 56, 78, 45, 21, 65]
with open('pokemon.txt', 'w') as pokemon_file:
    for pokemon_id in pokemon_ids:
        url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon_id)
        response = requests.get(url)
        pokemon_file.write(response.json()['name'] + ': ')

        pokemon_moves = response.json()['moves']

        for move in pokemon_moves:
            pokemon_file.write(move['move']['name'])
            pokemon_file.write(', ')

        pokemon_file.write('\n')
