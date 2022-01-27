"""
For web scraping Wordle to getting back hints
"""

import playwright


# WIP temperory function to get hints locally
def get_hints(guess: str):
    """Replicate wordle behaviour:\nChecks a guess against the answer and only returns hints"""

    word = "robot"  # for now
    hints = {i: None for i in range(5)}

    for i, letter in enumerate(guess):
        if letter in word and guess[i] == word[i]:
            hints[i] = True
            word = f"{word[:i]}.{word[i+1:]}"

    for i, letter in enumerate(guess):
        if letter in word and guess[i] != word[i]:
            if hints[i] != True:
                hints[i] = False
                word = word.replace(letter, ".", 1)

    return hints