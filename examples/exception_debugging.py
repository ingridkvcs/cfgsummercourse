# Add_vat applies VAT to a list of prices
# parameters:
#   - vat: integer between 1 and 100 (percentage)
#   - prices: list of numerical values (int, float)
from typing import Union


# User defined exception to indicate wrong type of VAT number
class VATNonStandardEror(Exception):
    pass


def add_vat(vat, prices):
    # Input validation using asserts
    assert (type(vat) == int)
    assert (vat > 0) # evaluates to True or False and Panic
    assert (type(prices) == list)
    assert (len(prices) > 0)
    # not working:
    # [assert (type(price) == int) for price in prices]
    # not working:
    # assert (type(price) == int for price in prices)
    # Working:
    for price in prices:
        assert type(price) in [int, float]
    # Iris: Only keep ints or floats in prices
    # valid_prices = [price for price in prices if type(price) == int or type(price) == float]
    # Check prices are > 0
    for price in prices:
        if price <= 0:
            raise ValueError("Price should be bigger than zero")
        if type(price) == float and price < 1:
            raise FloatingPointError("Decimal prices should be bigger than one")
    # Check VAT validity
    valid_vat = [5, 20]
    if vat not in valid_vat:
        raise VATNonStandardEror(f"VAT should be one of {valid_vat}")
    # Input is ok
    new_prices = [(price / 100 * vat) + price for price in prices]
    return new_prices

# Good input
# print(add_vat(1, [10, 20, 12, 2.45]))
# Bad input
# print(add_vat(0, [10, 20, 12, 2.45]))
# print(add_vat(1, []))
# print(add_vat([1], 21))
try:  # run a few lines of python
    #print(add_vat(21, ["st", 10, 233, {'a': 2, 'b': 3}]))
    # print(add_vat(21, [10, 0, 12, 245]))
    print(add_vat(1, [10, 11, 12]))
except TypeError as t:
    print(f"Invalid use of function: {t}")
except AssertionError: # do something if an exception was raised
    print("Failed to add_vat: assertion triggered")
except ValueError as v:
    print(f"Wrong input values {v}")
except FloatingPointError as a:
    print(f"Wrong input for arithmetic reasons {a}")
# custom Exception to check vat.
except VATNonStandardEror as vat:
    print(f"Non standard VAT: {vat}")
else: # do something if no exception was raised
    print("add_vat worked properly")
finally: # always run this
    print("end of program")
