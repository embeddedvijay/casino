import random

NUMBERS = [{"key": str(i), "label": str(i), "payout": 9} for i in range(10)]


def get_numbers():
    return NUMBERS


def pick_winner():
    return random.choice(NUMBERS)


def calculate_payout(bet_type: str, amount: float, winner: dict):
    if bet_type != winner["key"]:
        return 0.0

    return round(float(amount) * float(winner["payout"]), 2)