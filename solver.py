"""
Using wordguesser module to solve Wordle and Absurdle
"""

import re
import sys
import wordguesser
if __name__ != "__main__": from playwright import sync_api

playwright: object
browser: object
page: object


def init_browser():
    """"initialize the browser"""

    global playwright
    global browser
    global page

    playwright = sync_api.sync_playwright().start()
    browser = playwright.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()


class Wordle:
    """Class for Wordle solver"""

    URL = "https://www.nytimes.com/games/wordle/index.html"

    def scrape_hints(guess: str, i: int, **kwargs):
        """Scrape only the hints given a guess from the Wordle website"""

        # enter the guess and get the hint's inner html
        page.type("#board", f"{guess}\n")
        page.wait_for_timeout(2000)
        html = page.inner_html(f".row >> nth={i}")

        # if the guess is not in the list, delete it and return None as hints
        if "evaluation" not in html:
            for _ in range(5):
                page.keyboard.press("Backspace")
            return None

        # convert the inner html to hints in a dictionary
        evaluations = html.split("</game-tile>")[:-1]
        hints = {i: None for i in range(5)}
        for pos, _ in enumerate(guess):
            hint = re.search(r"evaluation=\"([a-z]*)\"", evaluations[pos])[1]

            if hint == "correct": hints[pos] = True
            elif hint == "present": hints[pos] = False
            elif hint == "absent": hints[pos] = None

        return hints

    def solve(hard_mode: bool = False):
        """Pass guess from guess_word to the Wordle website"""

        page.goto(Wordle.URL)
        if page.is_visible("#pz-gdpr-btn-closex"): page.click("#pz-gdpr-btn-closex") # close tracker pop up
        if page.is_visible(".close-icon"): page.click(".close-icon") # close tutorial pop up

        if hard_mode:  # enable hard mode from settings if requested
            page.click("#settings-button")
            page.click("#hard-mode")
            page.click("[icon=close]:visible")

        # printing the colorized guesses to the terminal
        for i, guess, hints in wordguesser.guess_word(Wordle.scrape_hints):
            if i == 5 and set(hints.values()) != {True}:
                print("Ran out of attempts")
                break
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")
        page.wait_for_timeout(2000)


class Absurdle:
    """Class for Absurdle solver"""

    URL = "https://qntm.org/files/absurdle/absurdle.html"

    def scrape_hints(guess: str, i: int, **kwargs):
        """Scrape only the hints given a guess from the Absurdle website"""

        # enter a guess and get the hint's inner html
        page.type(".absurdle__box1", f"{guess}\n")
        html = page.inner_html(f"tr >> nth={i}")

        # if the guess is not in the list, delete it and return None as hints
        if "--input" in html:
            for _ in range(5):
                page.keyboard.press("Backspace")
            return None

        # convert the inner html to hints in a dictionary
        evaluations = html.split("</td>")[:-1]
        hints = {i: None for i in range(5)}
        for pos, _ in enumerate(guess):
            hint = re.search(r"--([a-z].*)\"", evaluations[pos])[1]

            if hint == "exact": hints[pos] = True
            elif hint == "inexact": hints[pos] = False
            elif hint == "wrong": hints[pos] = None

        return hints

    def solve(hard_mode: bool = False):
        """Pass guess from guess_word to the Wordle website"""

        page.goto(Absurdle.URL)

        if hard_mode:  # enable hard mode from settings if requested
            page.click("text=\ufe0f")
            page.click("#hardModeCheckbox")
            page.click("text=\u2715")

        # printing the colorized guesses to the terminal
        for i, guess, hints in wordguesser.guess_word(Absurdle.scrape_hints):
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")
            if set(hints.values()) == {True}: page.wait_for_timeout(2000)


class Manual:
    """Class for solving Wordle with a coustom solution"""

    def get_solution():
        SOLUTION = input("Enter a solution to guess: ")

        while SOLUTION not in wordguesser.WORD_LIST:
            if len(SOLUTION) > 5:
                SOLUTION = input("Solution must be 6 letters long: ")
            else:
                SOLUTION = input("Solution must be in the wordlist: ")

        return SOLUTION

    def solve():
        """Let the wordguesser guess a manually provided solution"""

        SOLUTION = Manual.get_solution()
        for i, guess, hints in wordguesser.guess_word(
                wordguesser.generate_hints, solution=SOLUTION):
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")


if __name__ == "__main__":

    try: # check if playwright is installed else use manual mode
        from playwright import sync_api
    except ModuleNotFoundError:
        print("\nInstall Playwright to use on a browser: pip install playwright")
        print("Defaulting to manual mode\n")
        Manual.solve()
        sys.exit()

    print(
        "\nEnter '-w' to run the guessing algorithm on Wordle (IT MIGHT SPOIL TODAY'S WORDLE FOR YOU)\n"
        "Enter '-a' to run the guessing algorithm on Absurdle\n"
        "Enter '-m' to give the guessing algorithm a word of your own to guess\n"
        "(every word is allowed for manual therefore the average attempts required increases)\n"
    )

    try:
        hard_mode_choice = False

        # get the choice of the mode though input if not through an argument
        if len(sys.argv) > 1: choices = sys.argv[1:]
        else: choices = input("Choose a mode: ").strip().lower().split()

        if len(choices) > 0: mode_choice = choices[0]
        if len(choices) > 1: hard_mode_choice = choices[1]

        # check if the mode choice is valid
        while mode_choice not in ["-w", "-a", "-m"]:
            mode_choice = input("Not a valid choice try again: ")

        if mode_choice == "-w" or mode_choice == "-a": init_browser()
        if hard_mode_choice == "-h": hard_mode_choice = True

        if mode_choice == "-w": Wordle.solve(hard_mode=hard_mode_choice)
        elif mode_choice == "-a": Absurdle.solve(hard_mode=hard_mode_choice)
        elif mode_choice == "-m": Manual.solve()

    except KeyboardInterrupt:
        print("\nExiting...\n")
        playwright.stop() # not sure why this doesn't work
        raise SystemExit from None
