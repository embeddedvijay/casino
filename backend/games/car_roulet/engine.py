import random


CARS = [
    {"key": "BMW", "label": "BMW", "icon": "Ⓜ", "payout": 6},
    {"key": "AUDI", "label": "AUDI", "icon": "◎", "payout": 6},
    {"key": "TATA", "label": "TATA", "icon": "T", "payout": 6},
    {"key": "MERCEDES", "label": "MERCEDES", "icon": "✦", "payout": 6},
    {"key": "FERRARI", "label": "FERRARI", "icon": "♞", "payout": 6},
    {"key": "PORSCHE", "label": "PORSCHE", "icon": "♛", "payout": 6},
    {"key": "MAHINDRA", "label": "MAHINDRA", "icon": "〽", "payout": 6},
    {"key": "LUCKY", "label": "LUCKY", "icon": "★", "payout": 12},
]


def get_cars():
    return CARS


def pick_winner():
    r = random.random()

    if r < 0.08:
        return next(car for car in CARS if car["key"] == "LUCKY")

    return random.choice([car for car in CARS if car["key"] != "LUCKY"])


def calculate_payout(bet_type: str, amount: float, winner: dict):
    if bet_type != winner["key"]:
        return 0.0

    return round(float(amount) * float(winner["payout"]), 2)