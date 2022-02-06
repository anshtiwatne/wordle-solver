import unittest
import guesser


class TestGuesser(unittest.TestCase):
    """Tests for guesser.py"""

    def test_hints(self):
        """Test the get_hints function"""

        guesser.CHECK_WORD = "aabbb"

        guess = "aaabb"
        self.assertEqual(guesser.get_hints(guess), {
            0: True,
            1: True,
            2: None,
            3: True,
            4: True
        })
        guess = "bbaaa"
        self.assertEqual(guesser.get_hints(guess), {
            0: False,
            1: False,
            2: False,
            3: False,
            4: None
        })
        guess = "later"
        self.assertEqual(guesser.get_hints(guess), {
            0: None,
            1: True,
            2: None,
            3: None,
            4: None
        })

    def test_guesses(self):
        """Test the guesses from the guess_word function"""

        guesser.CHECK_WORD = "check"
        guesses = []
        for guess in guesser.guess_word():
            guesses.append(guess)
        last_guess = guesses[-1][0]
        self.assertEqual(guesser.CHECK_WORD, last_guess)


if __name__ == "__main__":
    unittest.main()