#!/usr/bin/env python3
#pylint: disable=invalid-name, no-self-argument, global-statement, unused-argument, no-method-argument, multiple-statements

"""
Using wordguesser module to solve Wordle and Absurdle
"""

import re
import sys

import wordguesser

playwright: object
browser: object
page: object

if __name__ != "__main__":
    from playwright import sync_api

    playwright: sync_api.Playwright
    browser: sync_api.Browser
    page: sync_api.Page


def init_browser():
    """"initialize the browser"""

    global playwright, browser, page

    playwright = sync_api.sync_playwright().start()
    browser = playwright.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()


class Wordle:
    """Class for Wordle solver"""

    URL = "https://www.nytimes.com/games/wordle/index.html"

    def scrape_hints(guess: str, i: int, **kwargs):
        """Scrape only the hints given a guess from the Wordle website"""

        # enter the guess and get the hint's inner html
        page.focus("#wordle-app-game")
        page.type("#wordle-app-game", f"{guess}")
        page.click(".Key-module_oneAndAHalf__bq8Tw")
        page.wait_for_timeout(2000)
        html = page.inner_html(f".Row-module_row__pwpBq >> nth={i}")

        # if the guess is not in the list, delete it and return None as hints
        if "tbd" in html:
            for _ in range(5):
                page.keyboard.press("Backspace")
            return None

        # convert the inner html to hints in a dictionary
        evaluations = re.findall(r"data-state=\"(.*?)\"", html)
        hints = {i: None for i in range(5)}
        for pos, _ in enumerate(guess):
            hint = evaluations[pos]

            match hint:
                case "correct": hints[pos] = True
                case "present": hints[pos] = False
                case "absent": hints[pos] = None

        return hints

    def solve(hard_mode: bool = False):
        """Pass guess from guess_word to the Wordle website"""

        page.goto(Wordle.URL)
        page.click('[data-testid="Play"]') # select play
        page.click('[data-testid="icon-close"]') # close tutorial pop up
        ad = page.query_selector("#ad-top") # remove ad to improve loading
        ad.evaluate("ad => ad.remove()")
        page.click(".Board-module_board__jeoPS")

        if hard_mode:  # enable hard mode from settings if requested
            page.click("#settings-button")
            page.click('[aria-label="Hard Mode"]')
            page.click(".game-icon >> visible=true")

        # page.wait_for_load_state()
        page.wait_for_timeout(3000)

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

            match hint:
                case "exact": hints[pos] = True
                case "inexact": hints[pos] = False
                case "wrong": hints[pos] = None

        return hints

    def solve(hard_mode: bool = False):
        """Pass guess from guess_word to the Wordle website"""

        page.goto(Absurdle.URL)

        if hard_mode: # enable hard mode from settings if requested
            page.click("text=\ufe0f")
            page.click("#hardModeCheckbox")
            page.click("text=\u2715")

        # printing the colorized guesses to the terminal
        for i, guess, hints in wordguesser.guess_word(Absurdle.scrape_hints):
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")
            if set(hints.values()) == {True}: page.wait_for_timeout(2000)


class Manual:
    """Class for solving Wordle with a custom solution"""

    def get_solution():
        """Take input for a solution to be guessed and validate it"""

        SOLUTION = input("Enter a solution to guess: ")

        while SOLUTION not in wordguesser.WORD_LIST:
            if len(SOLUTION) > 5:
                SOLUTION = input("Solution must be 6 letters long: ")
            else:
                SOLUTION = input("Solution must be in the word list: ")

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
        raise SystemExit from None

    print(
        "\nEnter '-w' to run the guessing algorithm on Wordle\n"
        "Enter '-a' to run the guessing algorithm on Absurdle\n"
        "Enter '-m' to give the guessing algorithm a word of your own to guess\n"
        "(The set of words is larger in the manual mode leading to higher average guesses)\n"
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

        match mode_choice:
            case "-w": Wordle.solve(hard_mode=hard_mode_choice)
            case "-a": Absurdle.solve(hard_mode=hard_mode_choice)
            case "-m": Manual.solve()

    except KeyboardInterrupt:
        print("\nExiting...\n")
        playwright.stop() # not sure why this doesn't work
        raise SystemExit from None
