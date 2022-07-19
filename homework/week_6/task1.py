"""

TASK 1

Write a class to represent a Cash Register.
Your class should keep the state of price total and purchased items

Below is a starter code:
------------------------
1. you can add new variables and function if you want to
2. you will NEED to add accepted method parameters where required.
For example, method add_item probably accepts some kind of item?.
3. You will need to write some examples of how your code works.

"""


class Item:

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name + ': ' + str(self.price)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name and self.price == other.price


class CashRegister:

    def __init__(self):
        self.total_items = []  # {'item': 'price'}
        self.total_price = 0
        self.discount = 0

    def add_item(self, item):
        self.total_items.append(item)
        self.total_price += item.price
        print("Added " + str(item))

    def remove_item(self, item):
        self.total_items.remove(item)
        self.total_price -= item.price
        print("Removed " + str(item))

    def apply_discount(self, amount):
        self.discount = amount
        print("Applied discount of " + str(amount))

    def get_total(self):
        return self.total_price - self.discount

    def show_items(self):
        print("Receipt")
        print("---------")
        for item in self.total_items:
            print(item)
        print("---------")

    def show_total(self):
        print("Total: " + str(self.get_total()))

    def reset_register(self):
        self.__init__()
        print("Next customer please!")


# EXAMPLE code run:

if __name__ == '__main__':
    register = CashRegister()
    register.add_item(Item("socks", 3))
    register.add_item(Item("t-shirt", 45))
    register.add_item(Item("shirt", 65))
    register.add_item(Item("shirt", 65))
    register.add_item(Item("hoodie", 20))

    register.show_items()
    register.remove_item(Item("shirt", 65))
    register.show_items()
    register.apply_discount(10)
    register.show_total()

    register.reset_register()
