"""
Guessing logic for Wordle
"""

from __future__ import annotations # type hints not supported before python 3.9
import copy
import dataclasses
import os
import random
# import re
import string
import colorama
from colorama import Fore
# from playwright.sync_api import sync_playwright

CHECK_WORD = "empty"
URL = "https://www.powerlanguage.co.uk/wordle/"
ABSPATH = os.path.join(os.path.dirname(__file__), "words.txt")
WORDLIST = list(open(ABSPATH).read().split())


def get_hints(guess: str):
    """Replicate wordle behaviour: Check a guess against the answer and only returns hints"""

    word = copy.copy(CHECK_WORD)
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


@dataclasses.dataclass
class LetterData:
    """Class for storing each letter's data"""
    known_positions: set = dataclasses.field(default_factory=set)
    impossible_positions: set = dataclasses.field(default_factory=set)
    min_count: int = 0
    count_frozen: bool = False


def build_letters_data(letters: dict[str, LetterData], guess: str, hints: dict):
    """Take the hints from wordle and add data accordingly to each letter's LetterData object"""

    yellows = {}

    for i, hint in hints.items():
        letter = guess[i]

        # letter is in the word and in the right position
        if hint is True:
            letters[letter].known_positions.add(i)
        # letter is in the word but not in the right position
        elif hint is False:
            letters[letter].impossible_positions.add(i)
            yellows[letter] = yellows.get(letter, 0) + 1
        # there is no more of the letter in the word
        elif hint is None:
            letters[letter].count_frozen = True

        # minimum count is positions in green + positions in yellow
        letters[letter].min_count = len(
            letters[letter].known_positions) + yellows.get(letter, 0)


def eliminate(possible_words: list[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in wordslist and remove it if it doesn't meet the requirements"""

    retained_words = copy.copy(possible_words)

    for word in possible_words:
        for i, letter in enumerate(word):

            if i in letters[guess[i]].known_positions and word[i] != guess[i]:
                retained_words.remove(word)
                break
            elif i in letters[letter].impossible_positions:
                retained_words.remove(word)
                break
            elif letters[letter].count_frozen is True:
                if word.count(letter) != letters[letter].min_count:
                    retained_words.remove(word)
                    break

        # check if all the yellows are present in the word in their possible positions
        if word not in retained_words: continue
        for letter in letters.keys():

            if not letters[letter].impossible_positions: continue
            elif letter not in word:
                retained_words.remove(word)
                break
            elif word.count(letter) < letters[letter].min_count:
                retained_words.remove(word)
                break

    return retained_words


def colorize(guess: str, hints: dict[int, str]):
    """Color the guess word based on it's hints"""
    colorama.init(autoreset=True)
    result = str()

    for i, hint in hints.items():
        letter = guess[i]
        if hint is True:
            result += f"{Fore.LIGHTGREEN_EX}{letter}{Fore.RESET}"
        elif hint is False:
            result += f"{Fore.LIGHTYELLOW_EX}{letter}{Fore.RESET}"
        elif hint is None:
            result += f"{Fore.LIGHTBLACK_EX}{letter}{Fore.RESET}"

    return result


def get_word():
    """Get the word for the guesses to check against"""

    CHECK_WORD = input("\nWord: ")

    while len(CHECK_WORD) != 5:
        print("Word must be 5 letters long")
        CHECK_WORD = input("\nTry again: ")

    while CHECK_WORD not in WORDLIST:
        print("Word not in list")
        CHECK_WORD = input("\nTry again: ")

    return CHECK_WORD


def main() -> list:
    """Guess the word, for every incorrect gets additional data gained to make a new guess"""

    guess = "later"
    hints = get_hints(guess)
    letters = {letter: LetterData() for letter in string.ascii_lowercase}
    possible_words = copy.copy(WORDLIST)
    yield guess, hints

    while set(hints.values()) != {True}:

        possible_words.remove(guess)
        build_letters_data(letters, guess, hints)
        possible_words = eliminate(possible_words, guess, letters)

        if not possible_words:
            raise IndexError("No possible words to choose from")
        guess = random.choice(possible_words)
        hints = get_hints(guess)

        yield guess, hints


if __name__ == "__main__":
    print(
        "\nChoose any five letter word and let the guesser guess your word\n")
    print("Green: letter is in the word and in the right position\n"
          "Yellow: letter is in the word but in the wrong position\n"
          "Gray: there is no more of the letter in the word\n")

    while True:
        CHECK_WORD = get_word()
        for guess, hints in main():
            print(colorize(guess, hints))
