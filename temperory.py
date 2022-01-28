"""
For web scraping Wordle to getting back hints
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from re import search
import time


url = "https://www.powerlanguage.co.uk/wordle/"

with sync_playwright() as sync:
    browser = sync.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto(url)
    page.click(".close-icon")

    def get_hints(guess: str):
        page.type("#board", f"{guess}\n")
        page.is_visible("#board")
        html = page.inner_html(":root")
        hints = {i: None for i in range(5)}
        soup = BeautifulSoup(html, "html.parser")
        print(html)

        return "test"
        for i, letter in enumerate(guess):
            hint = search(f"letter=\"{letter}\" evaluation=\"([a-z].*?)\"", html)[1]
            if hint == "correct": hints[i] = True
            elif hint == "present": hints[i] = False
            elif hint == "absent": hints[i] = None

        return hints

    print(get_hints("ratio"))
    #print(get_hints("ramen"))