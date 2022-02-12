"""
Script to run guesser on Wordle
"""

# RUNNING THIS MIGHT SPOIL TODAY'S WORDLE FOR YOU

import re
from playwright import sync_api
import wordguesser

URL = "https://www.nytimes.com/games/wordle/index.html"


def scrape_hints(guess: str, i: int, page: sync_api.Page, **kwargs):
    """Scrape only the hints given a guess from the Wordle website"""

    # enter the guess and get the hint's inner html
    page.type("#board", f"{guess}\n")
    page.wait_for_timeout(2000)
    html = page.inner_html(f".row >> nth={i}")

    # if the guess is not in the list, delete it and return None as hints
    if "evaluation" not in html:
        for _ in range(5): page.keyboard.press("Backspace")
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


def solve_wordle(hard_mode: bool = False):
    """Pass guess from guess_word to the Wordle website"""

    with sync_api.sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)

        # close the tutorial pop-up that appears on first load
        if page.is_visible(".close-icon"):
            page.click(".close-icon")

        # enable hard mode from settings if requested
        if hard_mode:
            page.click("#settings-button")
            page.click("#hard-mode")
            page.click("[icon=close]:visible")

        # printing the colorized guesses to the terminal
        for i, guess, hints in wordguesser.guess_word(scrape_hints, page):
            if i == 5 and set(hints.values()) != {True}:
                print("Ran out of attempts")
                break
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")


if __name__ == "__main__":
    solve_wordle(hard_mode=True)
