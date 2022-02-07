"""
WIP
"""

# pylint: disable=invalid-name, redefined-outer-name, multiple-statements

import copy
import json
import os
import string
from playwright.sync_api import sync_playwright
import guesser

URL = "https://www.powerlanguage.co.uk/wordle/"
ABSPATH = os.path.join(os.path.dirname(__file__), "words.txt")
WORDLIST = list(open(ABSPATH, encoding="utf-8").read().split())


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


def guess_word():
    """Guess the word, for every incorrect gets additional data gained to make a new guess"""

    guess = "apers"
    hints = guesser.generate_hints(guess, get_word())
    letters = {letter: guesser.LetterData() for letter in string.ascii_lowercase}
    possible_words = copy.copy(WORDLIST)
    yield guess, hints

    while set(hints.values()) != {True}:

        possible_words.remove(guess)
        guesser.build_letters_data(letters, guess, hints)
        possible_words = guesser.eliminate(possible_words, guess, letters)

        if not possible_words:
            raise IndexError("No possible words to choose from")
        guess = guesser.choose_word(possible_words)
        hints = guesser.generate_hints(guess)

        yield guess, hints


def solve_wordle():
    """Solve the current wordle using the guesser in a window"""

    with sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        page.click(".close-icon")

        def scrape_hints(i: int, guess: str):
            """Scrape only the hints given a guess from the Wordle website"""

            page.type("#board", f"{guess}\n")
            page.wait_for_timeout(2000)
            local_storage_js = "JSON.stringify(localStorage)"
            local_storage = json.loads(page.evaluate(local_storage_js))
            evaluations = json.loads(local_storage["gameState"])["evaluations"]
            evaluation = evaluations[i]

            if evaluation is None:
                for _ in range(5):
                    page.keyboard.press("Backspace")
                    page.wait_for_timeout(100)
                return None
            hints = {i: None for i in range(5)}
            for i, element in enumerate(evaluation):
                if element == "correct": hints[i] = True
                elif element == "present": hints[i] = False
                elif element == "absent": hints[i] = None

            return hints

        i = 0
        guess = "apers"
        hints = scrape_hints(i, guess)
        letters = {letter: guesser.LetterData() for letter in string.ascii_lowercase}
        possible_words = copy.copy(WORDLIST)

        while set(hints.values()) != {True}:
            i += 1

            possible_words.remove(guess)
            guesser.build_letters_data(letters, guess, hints)
            possible_words = guesser.eliminate(possible_words, guess, letters)

            if not possible_words:
                raise IndexError("No possible words to choose from")
            guess = guesser.choose_word(possible_words, randomize=True)
            hints = scrape_hints(i, guess)
            while hints == None:
                guess = guesser.choose_word(possible_words, randomize=True)
                hints = scrape_hints(i, guess)


if __name__ == "__main__":
    solve_wordle()