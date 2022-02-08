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

⬛⬛⬛🟨⬛ First guess is always "later" as it's statistically the best word to start with

🟨⬛⬛🟩🟨 Second guess is epoch sice there's no more of l, a, t and r but there's an e somewhere else

🟩🟩🟩🟩🟩 By the third guess the algorithm arrives at the solution using the same procedure as the second but with more data

On average for 25 random solutions the algorithm averaged 4.64 guesses to get the solution.

## Choosing words

Given a list of possible words, if you rank every word by what ratio match it is to every other word, you'll get a word that best represents all of the possible words therefore reducing the size of possible words.

```python
def choose_word(possible_words):

    for wordA in possible_words:
        for wordB in possible_words:
            shuffleable[wordA] = shuffleable.get(wordA, 0) + SequenceMatcher(
                None, wordA, wordB).ratio()

    return max(shuffleable, key=shuffleable.get)
```

Running the above code on the list of every five letter word in english will give you **later** a word that contains very common letters that appear a lot in other five letter words which should make it a really good first guess.

## Contributing

Send a pull request if you'd like to make a change or open an issue. You're free to use the guessing algorithm for your own implementations.

## License

[MIT](https://github.com/anshunderscore/wordle_solver/blob/main/LICENSE)