"""
Gussing logic for Wordle
"""
import os
print(os.getcwd())

from collections import Counter
from copy import copy
from dataclasses import dataclass
from random import choice
from re import findall, MULTILINE
from string import ascii_lowercase as alphabet


def get_hints(guess: str):

    word = "robot"
    word_copy = copy(word)
    hints = {i: None for i in range(5)}

    for i, letter in enumerate(guess):
        if letter in word and guess[i] != word[i]:
            hints[i] = False
            word = word.replace(letter, ".", 1)

    word = copy(word_copy)
    for i, letter in enumerate(guess):
        if letter in word and guess[i] == word[i]:
            hints[i] = True
            word = f"{word[:i]}.{word[i+1:]}"

    return hints


def to_colors(guess: str, hints: dict[int, str]) -> tuple[list]:
    green = dict()
    yellow = dict()
    gray = set()

    for i, hint in hints.items():
        letter = guess[i]
        if hint == True: green[i] = letter
        elif hint == False:
            value = yellow.get(letter, [])
            yellow[letter] = value + [i]
        elif hint == None: gray.add(letter)

    return (green, yellow, gray)


def eliminate(guess: str, words: list, green: dict, yellow: dict, gray: set) -> list:
    retained_words = copy(words)
    counter_green = Counter(green.values())

    def check_green():
        for position, letter in green.items():
            if guess[position] != letter:
                retained_words.remove(word)
                print("GREN")
                return True
        return False

    def check_yellow():
        for letter, positions in yellow.items():
            if guess.count(letter) < len(positions):
                for position in positions:
                    if guess[position] == letter:
                        retained_words.remove(word)
                        print("YELW")
                        return True
        return False

    def check_gray():
        for letter in gray:
            greens = counter_green.get(letter) if counter_green.get(letter) != None else 0
            yellows = len(yellow.get(letter)) if yellow.get(letter) != None else 0

            if letter in guess:
                if guess.count(letter) < greens + yellows:
                    retained_words.remove(word)
                    print("GRAY")
                    return True
        return False
        
    
    for word in words:
        if check_green(): continue
        if check_yellow(): continue
        if check_gray(): continue

    return retained_words

# debug function
def run():
    with open("words.txt") as file:
        words = findall(r"^[a-z]{5}$", file.read(), flags=MULTILINE)
    print(len(words))
    guess = "ratio"
    hints = get_hints(guess)
    green, yellow, gray = to_colors(guess, hints)
    words = eliminate(guess, words, green, yellow, gray)
    print(len(words))

if __name__ == "__main__":
    run()