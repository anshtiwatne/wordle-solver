"""
Guessing logic for Wordle
"""

from copy import copy
from colorama import init, Fore
from os import path
from random import choice
from string import ascii_lowercase
from scraper import get_hints


class LetterData:
    def __init__(self) -> None:
        self.known_positions = set()
        self.impossible_positions = set()
        self.min_count = int()
        self.count_frozen = bool()


def build_letters_data(letters: dict[str, LetterData], guess: str):
    """Take the hints from wordle and add data accordingly to each letter's LetterData object"""

    hints = get_hints(guess)
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


def eliminate(words: set[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in words and remove it if it doesn't meet the requirements"""

    retained_words = copy(words)

    for word in words:
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


def guess_word() -> str:
    """Guess the word, for every incorrect gets additional data gained to make a new guess"""

    guess = "ratio"  # first guess to start the game
    hints = get_hints(guess)
    letters = {letter: LetterData() for letter in list(ascii_lowercase)}
    abspath = path.join(path.dirname(__file__), "words.txt")
    words = [word for word in open(abspath).read().split()]
    guesses = [guess]

    while set(hints.values()) != {True}:
        words.remove(guess)
        build_letters_data(letters, guess)
        words = eliminate(words, guess, letters)

        guess = choice(words)
        hints = get_hints(guess)
        guesses.append(guess)

    return guesses


if __name__ == "__main__":
    init(autoreset=True)
    result = str()

    guesses = guess_word()
    for i, guess in enumerate(guesses):
        result += f"{i + 1}. "
        hints = get_hints(guess)
        for i, hint in hints.items():
            letter = guess[i]
            if hint == True: result += f"{Fore.LIGHTGREEN_EX}{letter}{Fore.RESET}"
            elif hint == False: result += f"{Fore.LIGHTYELLOW_EX}{letter}{Fore.RESET}"
            elif hint == None: result += f"{Fore.LIGHTBLACK_EX}{letter}{Fore.RESET}"
        result += "\n"
    result = result[:-1]
    
    print(result)