"""
Script to run guesser on Wordle
"""

# RUNNING THIS MIGHT SPOIL TODAY'S WORDLE FOR YOU

import json
import playwright.sync_api as sync_api
import wordguesser

URL = "https://qntm.org/files/absurdle/absurdle.html"


def scrape_hints(page: sync_api.Page, i: int, guess: str):
    """Scrape only the hints given a guess from the Wordle website"""

    page.type(".absurdle__box1", f"{guess}\n")
    page.wait_for_timeout(2000)
    local_storage_js = "JSON.stringify(localStorage)"
    local_storage = json.loads(page.evaluate(local_storage_js))
    evaluations = json.loads(local_storage["gameState"])["evaluations"]
    evaluation = evaluations[i]

    if evaluation is None:
        for _ in range(5):
            page.keyboard.press("Backspace")
        return None

    hints = {i: None for i in range(5)}
    for i, element in enumerate(evaluation):
        if element == "correct": hints[i] = True
        elif element == "present": hints[i] = False
        elif element == "absent": hints[i] = None

    return hints


def solve_absurdle(hard_mode: bool = False):
    """Pass guess from guess_word to the Wordle website"""

    with sync_api.sync_playwright() as sync:
        browser = sync.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        get_hints = scrape_hints

        if hard_mode:
            page.click("text=\ufe0f")
            page.click("#hardModeCheckbox")
            page.click("text=\u2715")

        for i, guess, hints in wordguesser.guess_word(page, get_hints):
            if i == 5 and set(hints.values()) != {True}:
                print("Ran out of attempts")
                break
            print(f"{i+1}. {wordguesser.colorize(guess, hints)}")


if __name__ == "__main__":
    solve_absurdle(hard_mode=True)
