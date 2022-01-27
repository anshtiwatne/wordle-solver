"""
WIP :P
"""

from colorama import init, Fore
import guesser

def manual():
    word = input("Word: ")
    guesser.check_word = word
    result = str()
    guesses = guesser.guess_word()
    init(autoreset=True)

    for i, guess in enumerate(guesses):
        result += f"{i + 1}. "
        hints = guesser.get_hints(guess)
        for i, hint in hints.items():
            letter = guess[i]
            if hint == True: result += f"{Fore.LIGHTGREEN_EX}{letter}{Fore.RESET}"
            elif hint == False: result += f"{Fore.LIGHTYELLOW_EX}{letter}{Fore.RESET}"
            elif hint == None: result += f"{Fore.LIGHTBLACK_EX}{letter}{Fore.RESET}"
        result += "\n"
    result = result[:-1]

    print(result)


def scraper():
    print("WIP :(")


def run_mode():
    choice = input("\nEnter W for solving Wordle using guesser or C to challenge the gusser to guess your own word: ").strip().lower()
    if choice == "w": scraper()
    elif choice == "c": manual()


if __name__ == "__main__":
    run_mode()