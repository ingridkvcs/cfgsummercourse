def is_within_range(num, _min, _max):
    if _min <= num <= max:
        return True
    else:
        return False

def is_even (num):
    return num % 2 == 0


def red_or_blue (num):
    if not is_even(num):
        return 'Red'
    else:
        if is_within_range(num, 6, 20):
            return 'Red'
        elif is_within_range(num, 2, 5) or num > 20:
            return 'Blue'
