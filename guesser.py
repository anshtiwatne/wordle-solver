"""
Guessing logic for Wordle
"""

# pylint: disable=invalid-name, redefined-outer-name, multiple-statements

import copy
import dataclasses
import random
from difflib import SequenceMatcher
import colorama
from colorama import Fore


def generate_hints(guess: str, solution: str):
    """Replicate wordle behaviour: Check a guess against the answer and only returns hints"""

    word = copy.copy(solution)
    hints = {i: None for i in range(5)}

    for i, letter in enumerate(guess):
        if letter in word and guess[i] == word[i]:
            hints[i] = True
            word = f"{word[:i]}.{word[i+1:]}"

    for i, letter in enumerate(guess):
        if letter in word and guess[i] != word[i]:
            if hints[i]: continue
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


def build_letters_data(letters: dict, guess: str, hints: dict):
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


def eliminate(possible_words: list, guess: str, letters: dict):
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


def choose_word(possible_words: list, randomize: bool = False):
    """Get an optimized choice of a word to be the next guess from the possible words"""

    if randomize: return random.choice(possible_words)
    shuffleable = {}
    # The best next guess seems to be the one that can shuffle in the most other possible words
    # since this maximizes the amount of green and yellow hints you get
    
    for wordA in possible_words:
        for wordB in possible_words:
            shuffleable[wordA] = shuffleable.get(wordA, 0) + SequenceMatcher(None, wordA, wordB).ratio()

    return max(shuffleable, key=shuffleable.get)


def colorize(guess: str, hints: dict):
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
