# def is_palindrome(value):
#     if value == value[::-1]:
#         return True
#     else:
#         return False


# def is_palindrome(value):
#     if value is None:
#         return False
#     value = value.lower()
#     value = value.strip()
#     if not value:
#         return False
#
#     return value == value[::-1]

def is_palindrome(value):
    if not value:
        return False

    value = value.strip().lower()

    if value == '':
        return False

    for i in range(int(len(value)/2)):
        if value[i] != value[len(value)-1-i]:
            return False

    return True


