"""
Guessing logic for Wordle
"""

from copy import copy
from re import findall, MULTILINE
from random import choice
from string import ascii_lowercase as alphabet
from subprocess import REALTIME_PRIORITY_CLASS

class LetterData:
    def __init__(self) -> None:
        self.known_positions = set()
        self.possible_positions = {i for i in range(5)}
        self.min_count = int()
        self.count_frozen = bool()
        self.yellow = bool()
        self.yellow_count = int()


def build_letters_data(letters: dict[str, LetterData], guess: str):
    """Take the hints from wordle and adds data accordingly to each letter's Match object"""

    hints = get_hints(guess)

    for i, hint in hints.items():
        letter = guess[i]

        if hint == True:
            # letter is in the right position and there's one more of the letter
            letters[letter].known_positions.add(i)
            letters[letter].min_count += 1
        elif hint == False:
            # letter is in the wrong position and there's one more of the letter
            letters[letter].possible_positions.remove(i)
            letters[letter].min_count += 1
            letters[letter].yellow = True
            letters[letter].yellow_count += 1
        elif hint == None:
            # letter is in the wrong position and there's no more of the letter
            letters[letter].possible_positions.remove(i)
            letters[letter].count_frozen = True


def eliminate(words: set[str], guess: str, letters: dict[str, LetterData]):
    """Check every word in words and remove it based on the data for every letter's match data"""

    retained_words = copy(words)

    for word in words:
        for i, letter in enumerate(word):

            if i in letters[guess[i]].known_positions and word[i] != guess[i]:
                retained_words.remove(word)
                break

            elif i not in letters[letter].possible_positions:
                retained_words.remove(word)
                break

            elif letters[letter].count_frozen == True:
                if word.count(letter) != letters[letter].min_count:
                    retained_words.remove(word)
                    break
                
        if word in retained_words:
            for letter in letters.keys():
                if letters[letter].yellow:
                    if letter in word:
                        if word.count(letter) < letters[letter].yellow_count:
                            retained_words.remove(word)
                            break
                    else:
                        retained_words.remove(word)
                        break
                        

    return retained_words


def guess_word() -> str:
    """Guess the word, for every incorrect guess additional data gained to make a new guess"""

    guess = "ratio"  # first guess to start the game
    hints = get_hints(guess)
    print(guess)
    letters = {letter: LetterData() for letter in list(alphabet)}

    with open("words.txt") as file:
        words = list(findall(r"^[a-z]{5}$", file.read(), flags=MULTILINE))

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