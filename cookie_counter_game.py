"""Fisher Price Vintage Cookie Counter Toy (1985) inspired counting game."""

from __future__ import annotations

import random

ROUNDS = 5
MIN_COOKIES = 1
MAX_COOKIES = 12


def play_round(round_number: int) -> bool:
    cookies = random.randint(MIN_COOKIES, MAX_COOKIES)
    print(f"Round {round_number}: How many cookies are on the counter?")
    print("🍪 " * cookies)

    while True:
        guess = input("Your count: ").strip()
        if not guess:
            print("Please enter a number.")
            continue
        if not guess.isdigit():
            print("Numbers only, please.")
            continue
        break

    return int(guess) == cookies


def main() -> None:
    print("Fisher Price Cookie Counter (1985) - Counting Game")
    print(f"Count the cookies across {ROUNDS} rounds.\n")

    score = 0
    for round_number in range(1, ROUNDS + 1):
        if play_round(round_number):
            score += 1
            print("Correct!\n")
        else:
            print("Not quite. Keep counting!\n")

    print(f"Game over! You got {score} out of {ROUNDS} correct.")


if __name__ == "__main__":
    main()
