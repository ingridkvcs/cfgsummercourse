with open('file_handling_astronauts.txt', 'r') as fh:
    text = fh.read()

    count = 0
    for letter in text:
        if letter.isupper():
            count += 1
    print(count)
