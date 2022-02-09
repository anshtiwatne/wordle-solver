# Wordle Solver

Guessing algrorithm for Wordle written in Python

## Installation & Usage

Either download and run the published exe or run guesser.py maunally

```bash
python3 guesser.py

later
epoch
check
```

## How it works

Once the algorithm has hints for a guess, it converts them into match data (known positions, impossible positions, minimum count and if there could be any more of the letter) for every letter in the alphablet which.

Then based on each letter's match data words from the list of all possible words are removed therefore shortening the list.

After the list of possible words is shortend a word is chosen through the choose_word function to be the new guess to then get hints for and shorten the possiblities further.

With the solution as "check":

⬛⬛⬛🟨⬛ First guess is later in this case

🟨⬛⬛🟩🟨 Second guess is epoch sice there's no more of l, a, t and r but there's an e somewhere else

🟩🟩🟩🟩🟩 By the third guess the algorithm arrives at the solution using the same procedure as the second but with more data

On average for 25 random solutions the algorithm averaged 4.64 guesses to get the solution.

## Choosing words

Given a list of possible words, if you rank every word by what ratio match it is to every guess made till now, you'll get a word that adds the maximum amount of new letters and positions to the existing pool of letters.

```python
def choose_word(guesses: list, possible_words: list, randomize: bool = False):
    """Get an optimized choice of a word to be the next guess from the possible words"""

    if randomize: return random.choice(possible_words)
    comparison = {}
    # The best next guess seems to be the one that differs most from the previous guesses
    # since this diversifys the letters used therefore maximizing the hints received

    for word in possible_words:
        for guess in guesses:
            # get the similarity between the word and the guess
            comparison[word] = comparison.get(word, 0) + SequenceMatcher(None, word, guess).ratio()
        # number of total letters - number of unique letters
        comparison[word] = comparison.get(word, 0) + len(word) - len(set(word))

    return min(comparison, key=comparison.get)
```

## Contributing

Send a pull request if you'd like to make a change or open an issue. You're free to use the guessing algorithm for your own implementations.

## License

[MIT](https://github.com/anshunderscore/wordle_solver/blob/main/LICENSE)