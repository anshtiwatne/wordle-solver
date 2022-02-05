# Wordle Solver

Guessing algrorithm for Wordle written in Python

## Installation & Usage

Either download and run the published exe or install the required modules and run guesser.py manually. Then input a word for the algorithm to guess (it only uses the word provided to check against and get hints).

```bash
python3 guesser.py

Word: check
later
epoch
check
```

## How it works

Once the algorithm has hints for a guess, it converts them into match data (known positions, impossible positions, minimum count and if there could be any more of the letter) for every letter in the alphablet which.

Then based on each letter's match data words from the list of all possible words are removed therefore shortening the list.

After the list of possible words is shortend a word is randomly picked (can be optimized in the future) to be the new guess to then get hints for and shorten the possiblities further.

With the solution as "check":

⬛⬛⬛🟨⬛ First guess is always later as it's statistically the best word to start with

🟨⬛⬛🟩🟨 Second guess is epoch sice there's no more of l, a, t and r but there's an e somewhere else

🟩🟩🟩🟩🟩 By the third guess the algorithm arrives at the solution using the same procedure as the second but with more data

## Contributing

Send a pull request if you'd like to make a change or open an issue. You're free to use the guessing algorithm for your own implementations.

## License

[MIT](https://github.com/anshunderscore/wordle_solver/blob/main/LICENSE)