def longest_word(words):
    wrd = words[0]
    for item in words:
        if len(wrd) < len(item):
            wrd = item

    return wrd

animals = ['cat', 'horse', 'elephant', 'dog']

print(longest_word(animals))

