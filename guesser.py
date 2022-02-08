"""
Guessing logic for Wordle
"""

# pylint: disable=invalid-name, redefined-outer-name, multiple-statements

import copy
import dataclasses
import json
import os
import random
from difflib import SequenceMatcher
import string
import colorama
from colorama import Fore
import playwright.sync_api as sync_api

URL = "https://www.powerlanguage.co.uk/wordle/"
ABSPATH = os.path.join(os.path.dirname(__file__), "words.txt")
WORDLIST = list(open(ABSPATH, encoding="utf-8").read().split())


def generate_hints(guess: str, solution: str):
    """Replicate wordle behaviour: Check a guess against the answer and only returns hints"""
    # Extra function, not currently used

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
            shuffleable[wordA] = shuffleable.get(wordA, 0) + SequenceMatcher(
                None, wordA, wordB).ratio()

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


def scrape_hints(page: sync_api.Page, i: int, guess: str):
    """Scrape only the hints given a guess from the Wordle website"""

    if i >= 5: raise IndexError("Ran out of attempts")
    page.type("#board", f"{guess}\n")
    page.wait_for_timeout(2000)
    local_storage_js = "JSON.stringify(localStorage)"
    local_storage = json.loads(page.evaluate(local_storage_js))
    evaluations = json.loads(local_storage["gameState"])["evaluations"]
    evaluation = evaluations[i]

    if evaluation is None:
        for _ in range(5):
            page.keyboard.press("Backspace")
            page.wait_for_timeout(75)
        return None

    hints = {i: None for i in range(5)}
    for i, element in enumerate(evaluation):
        if element == "correct": hints[i] = True
        elif element == "present": hints[i] = False
        elif element == "absent": hints[i] = None

    return hints


def guess_word(page: sync_api.Page):
    """Yeilds a guess until the guess matches the solution"""

    i = int()
    guess = "apers" # statistically the best guess to start Wordle with
    hints = scrape_hints(page, i, guess)
    letters = {letter: LetterData() for letter in string.ascii_lowercase}
    possible_words = copy.copy(WORDLIST)
    yield guess, hints

    while set(hints.values()) != {True}:
        i += 1
        possible_words.remove(guess)
        build_letters_data(letters, guess, hints)
        possible_words = eliminate(possible_words, guess, letters)

        if not possible_words:
            raise IndexError("No possible words left")
        guess = choose_word(possible_words, randomize=True)
        hints = scrape_hints(page, i, guess)

        while hints is None:
            possible_words.remove(guess)
            guess = choose_word(possible_words, randomize=True)
            hints = scrape_hints(page, i, guess)

        yield guess, hints


def solve_wordle():
    """Passes guesses from"""

    with sync_api.sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        page.click(".close-icon")
        page.focus("#board")

        for guess, hints in guess_word(page):
            print(colorize(guess, hints))


if __name__ == "__main__": solve_wordle()
