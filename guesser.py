"""
Guessing logic for Wordle
"""

from colorama import init, Fore
from copy import copy
from dataclasses import dataclass, field
from os import path
# from playwright.sync_api import sync_playwright
from random import choice
from re import search
from string import ascii_lowercase

check_word = "empty"
abspath = path.join(path.dirname(__file__), "words.txt")
wordlist = [word for word in open(abspath).read().split()]
url = "https://www.powerlanguage.co.uk/wordle/"


def get_hints(guess: str):
    """Replicate wordle behaviour: Check a guess against the answer and only returns hints"""

    word = copy(check_word)
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


@dataclass
class LetterData:
    """Class for storing each letter's data"""
    known_positions: set = field(default_factory=set)
    impossible_positions: set = field(default_factory=set)
    min_count: int = 0
    count_frozen: bool = False


def build_letters_data(letters: dict[str, LetterData], guess: str, hints: dict):
    """Take the hints from wordle and add data accordingly to each letter's LetterData object"""

    yellows = dict()

    for i, hint in hints.items():
        letter = guess[i]

        # letter is in the word and in the right position
        if hint == True:
            letters[letter].known_positions.add(i)
        # letter is in the word but not in the right position
        elif hint == False:
            letters[letter].impossible_positions.add(i)
            yellows[letter] = yellows.get(letter, 0) + 1
        # there is no more of the letter in the word
        elif hint == None:
            letters[letter].count_frozen = True

        # minimum count is positions in green + positions in yellow
        letters[letter].min_count = len(
            letters[letter].known_positions) + yellows.get(letter, 0)


def eliminate(possible_words: list[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in wordslist and remove it if it doesn't meet the requirements"""

    retained_words = copy(possible_words)

    for word in possible_words:
        for i, letter in enumerate(word):

            if i in letters[guess[i]].known_positions and word[i] != guess[i]:
                retained_words.remove(word)
                break
            elif i in letters[letter].impossible_positions:
                retained_words.remove(word)
                break
            elif letters[letter].count_frozen == True:
                if word.count(letter) != letters[letter].min_count:
                    retained_words.remove(word)
                    break

        # check if all the yellows are present in the word in their possible positions
        if word in retained_words:
            for letter in letters.keys():
                if letters[letter].impossible_positions:
                    if letter in word:
                        if word.count(letter) < letters[letter].min_count:
                            retained_words.remove(word)
                            break
                    else:
                        retained_words.remove(word)
                        break

    return retained_words


def colorize_guess(guess: str, hints: dict[int, str]):
    """Color the guess word based on it's hints"""
    init(autoreset=True)
    result = str()

    for i, hint in hints.items():
        letter = guess[i]
        if hint == True: result += f"{Fore.LIGHTGREEN_EX}{letter}{Fore.RESET}"
        elif hint == False:
            result += f"{Fore.LIGHTYELLOW_EX}{letter}{Fore.RESET}"
        elif hint == None:
            result += f"{Fore.LIGHTBLACK_EX}{letter}{Fore.RESET}"

    return result


def guess_word() -> list:
    """Guess the word, for every incorrect gets additional data gained to make a new guess"""

    guess = "ratio"
    hints = get_hints(guess)
    letters = {letter: LetterData() for letter in list(ascii_lowercase)}
    possible_words = copy(wordlist)
    yield guess, hints

    while set(hints.values()) != {True}:

        possible_words.remove(guess)
        build_letters_data(letters, guess, hints)
        possible_words = eliminate(possible_words, guess, letters)

        guess = choice(possible_words)
        hints = get_hints(guess)

        yield guess, hints


def get_word():
    """Get the word for the guesses to check against"""

    check_word = input("\nWord: ")

    while len(check_word) != 5:
        print("Word must be 5 letters long")
        check_word = input("\nTry again: ")

    while check_word not in wordlist:
        print("Word not in list")
        check_word = input("\nTry again: ")

    return check_word


if __name__ == "__main__":
    print("\nChoose any five letter word and let the guesser guess your word\n")
    print("Green: letter is in the word and in the right position")
    print("Yellow: letter is in the word but in the wrong position")
    print("Gray: there is no more of the letter in the word")

    while True:
        try:
            check_word = get_word()
            for guess, hints in guess_word():
                print(colorize_guess(guess, hints))
        except KeyboardInterrupt:
            print("Exiting...")
            break