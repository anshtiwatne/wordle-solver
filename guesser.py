"""
Guessing logic for Wordle
"""

from copy import copy
from re import findall, MULTILINE
from random import choice
from string import ascii_lowercase as alphabet
from scraper import get_hints

class LetterData:
    def __init__(self) -> None:
        self.known_positions = set()
        self.impossible_positions = set()
        self.min_count = int()
        self.count_frozen = bool()
        # not required
        self.yellow = bool()
        self.yellow_count = int()


def build_letters_data(letters: dict[str, LetterData], guess: str):
    """Take the hints from wordle and adds data accordingly to each letter's Match object"""

    hints = get_hints(guess)
    yellows = dict()

    for i, hint in hints.items():
        letter = guess[i]

        if hint == True:
            letters[letter].known_positions.add(i)
        elif hint == False:
            letters[letter].impossible_positions.add(i)
            yellows[letter] = yellows.get(letter, 0) + 1
        elif hint == None:
            letters[letter].count_frozen = True

        letters[letter].min_count = len(letters[letter].known_positions) + yellows.get(letter, 0)


def eliminate(words: set[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in words and remove it based on the data for every letter's match data"""

    retained_words = copy(words)

    for word in words:
        for i, letter in enumerate(word):

            if i in letters[guess[i]].known_positions and word[i] != guess[i]:
                retained_words.remove(word)
                if word == "robot": print(letter, word, "eeeeee")
                break

            elif i in letters[letter].impossible_positions:
                retained_words.remove(word)
                if word == "robot": print(letter, word, "ffffff")
                break

            elif letters[letter].count_frozen == True:
                if word.count(letter) != letters[letter].min_count:
                    retained_words.remove(word)
                    if word == "robot": print(letter, word, "gggggg", letters[letter].min_count)
                    break

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
    """Guess the word, for every incorrect guess additional data gained to make a new guess"""

    guess = "ratio"  # first guess to start the game torta
    hints = get_hints(guess)
    print(guess)
    letters = {letter: LetterData() for letter in list(alphabet)}
    words = [word for word in open("words.txt").read().split()]

    while set(hints.values()) != {True}:
        words.remove(guess)
        build_letters_data(letters, guess)
        words = eliminate(words, guess, letters)

        try:
            guess = choice(words)
            hints = get_hints(guess)
            print(guess)
        except IndexError:
            print("OUT OF WORDS")
            break

    return guess


if __name__ == "__main__":
    guess_word()