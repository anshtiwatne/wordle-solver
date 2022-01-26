"""
For web scraping Wordle to getting back hints
"""

from copy import copy
import playwright


# temperory function to get hints locally
def get_hints(guess: str):
    """Replicate wordle behaviour:\nChecks a guess against the answer and only returns hints"""

    word = "robot"
    word_copy = copy(word)
    hints = {i: None for i in range(5)}

    for i, letter in enumerate(guess):
        # if letter is yellow
        if letter in word and guess[i] != word[i]:
            hints[i] = False
            word = word.replace(letter, ".", 1)
        # if lettter is green

    word = copy(word_copy)
    for i, letter in enumerate(guess):
        if letter in word and guess[i] == word[i]:
            hints[i] = True
            word = f"{word[:i]}.{word[i+1:]}"
        # if letter is gray the hint remains unchanged

    return hints