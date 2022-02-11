"""
Script to run guesser on Absurdle
"""

import re
import playwright.sync_api as sync_api
import wordguesser

URL = "https://qntm.org/files/absurdle/absurdle.html"


def scrape_hints(page: sync_api.Page, i: int, guess: str):
    """Scrape only the hints given a guess from the Absurdle website"""

    page.type(".absurdle__box1", f"{guess}\n")
    html = page.inner_html(f"tr >> nth={i}")

    if "--input" in html:
        for _ in range(5): page.keyboard.press("Backspace")
        return None

    evaluations = html.split("</td>")[:-1]
    hints = {i: None for i in range(5)}
    for pos, _ in enumerate(guess):
        hint = re.search(r"--([a-z].*)\"", evaluations[pos])[1]

        if hint == "exact": hints[pos] = True
        elif hint == "inexact": hints[pos] = False
        elif hint == "wrong": hints[pos] = None

    return hints


def solve_absurdle(hard_mode: bool = False):
    """Pass guess from guess_word to the Wordle website"""

    with sync_api.sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)

        if hard_mode:
            page.click("text=\ufe0f")
            page.click("#hardModeCheckbox")
            page.click("text=\u2715")

        for i, guess, hints in wordguesser.guess_word(scrape_hints, page):
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")
            if set(hints.values()) == {True}: page.wait_for_timeout(2000)


if __name__ == "__main__":
    solve_absurdle(hard_mode=True)
