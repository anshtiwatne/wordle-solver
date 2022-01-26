"""
Guessing logic for Wordle
"""

from copy import copy
from dataclasses import dataclass
from re import findall, MULTILINE
from random import choice
from string import ascii_lowercase as alphabet

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


@dataclass
class Match:
    """Store all information for the letter in a Match object"""
    def __init__(self) -> None:
        self.known_positions = set()
        self.possible_positions = {i for i in range(5)}
        self.count = int()
        self.count_exact = bool()


def populate_match_data(letters: dict[str, Match], hints: dict, guess: str):
    """Take the hints from wordle and adds data accordingly to each letter's Match object"""

    for i, hint in hints.items():
        letter = guess[i]

        try:
            if hint == True:
                # letter is in the right position and there's one more of the letter
                letters[letter].known_positions.add(i)
                letters[letter].count += 1
            elif hint == False:
                # letter is in the wrong position and there's one more of the letter
                letters[letter].possible_positions.remove(i)
                letters[letter].count += 1
            elif hint == None:
                # letter is in the wrong position and there's no more of the letter
                letters[letter].possible_positions.remove(i)
                letters[letter].count_exact = True
        except KeyError:
            pass

    return letters


def eliminate(words: set[str], guess: str, letters: dict[str, Match]):
    """Check every word in words and remove it based on the data for every letter's match data"""

    retained_words = copy(words)

    for word in words:
        for i, letter in enumerate(word):
            # letter is in green but not in the right position
            if i in letters[guess[i]].known_positions and word[i] != guess[i]:
                    retained_words.remove(word)
                    break
            # letter is not in the possible positions
            elif i not in letters[letter].possible_positions:
                retained_words.remove(word)
                break
            # letter is not equal to its exact count
            elif letters[letter].count_exact == True:
                if word.count(letter) != letters[letter].count:
                    retained_words.remove(word)
                    break

    return retained_words


def guess_word() -> str:
    """Guess the word, for every incorrect guess additional data gained to make a new guess"""

    guess = "ratio"  # first guess to start the game
    hints = get_hints(guess)
    print(guess)
    letters = {letter: Match() for letter in list(alphabet)}

    with open(r"C:\\Users\\ansht\\VSCode-Docs\\wordle\\words.txt") as file:
        words = list(findall(r"^[a-z]{5}$", file.read(), flags=MULTILINE))

    while set(hints.values()) != {True}:
        words.remove(guess)
        letters = populate_match_data(letters, hints, guess)
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