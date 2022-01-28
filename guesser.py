"""
Guessing logic for Wordle
"""

from copy import copy
from colorama import init, Fore
from os import path
from playwright.sync_api import sync_playwright
from random import choice
from re import search
from string import ascii_lowercase

check_word = "empty"
url = "https://www.powerlanguage.co.uk/wordle/"


def get_local_hints(guess: str):
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


class LetterData:
    def __init__(self) -> None:
        self.known_positions = set()
        self.impossible_positions = set()
        self.min_count = int()
        self.count_frozen = bool()


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


def eliminate(wordlist: list[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in wordslist and remove it if it doesn't meet the requirements"""

    retained_words = copy(wordlist)

    for word in wordlist:
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


def guess_word() -> list:
    """Guess the word, for every incorrect gets additional data gained to make a new guess"""

    with sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.goto(url)
        page.click(".close-icon")

        def get_wordle_hints(guess: str):
            page.type("#board", f"{guess}\n")
            page.is_visible("#board")
            html = page.inner_html(".row")
            hints = {i: None for i in range(5)}

            for i, letter in enumerate(guess):
                hint = search(f"letter=\"{letter}\" evaluation=\"([a-z].*?)\"", html)[1]
                if hint == "correct": hints[i] = True
                elif hint == "present": hints[i] = False
                elif hint == "absent": hints[i] = None

            return hints

        guess = "ratio"  # first guess to start the game
        hints = get_wordle_hints(guess)
        letters = {letter: LetterData() for letter in list(ascii_lowercase)}
        abspath = path.join(path.dirname(__file__), "words.txt")
        wordlist = [word for word in open(abspath).read().split()]
        guesses = [guess]

        while set(hints.values()) != {True}:
            wordlist.remove(guess)
            build_letters_data(letters, guess, hints)
            wordlist = eliminate(wordlist, guess, letters)

            guess = choice(wordlist)
            hints = get_wordle_hints(guess)
            guesses.append(guess)
            
        return guesses


if __name__ == "__main__":
    guess_word()

if __name__ != "__main__":
    guess_word
    quit()

    init(autoreset=True)
    result = str()
    guesses = guess_word()

    for i, guess in enumerate(guesses):
        result += f"{i + 1}. "
        hints = get_wordle_hints(guess)

        for i, hint in hints.items():
            letter = guess[i]
            if hint == True: result += f"{Fore.LIGHTGREEN_EX}{letter}{Fore.RESET}"
            elif hint == False: result += f"{Fore.LIGHTYELLOW_EX}{letter}{Fore.RESET}"
            elif hint == None: result += f"{Fore.LIGHTBLACK_EX}{letter}{Fore.RESET}"
        result += "\n"

    result = result[:-1]
    print(result)