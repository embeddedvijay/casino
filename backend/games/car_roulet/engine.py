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


# Round table track sequence.
# Isme repeated icons hain, jaise screenshot mein top track par car logos repeated hote hain.
TRACK_SEQUENCE_KEYS = [
    "PORSCHE",
    "BMW",
    "MAHINDRA",
    "AUDI",
    "TATA",
    "LUCKY",
    "BMW",
    "MAHINDRA",
    "AUDI",
    "TATA",
    "MERCEDES",
    "FERRARI",
    "PORSCHE",
    "MERCEDES",
    "BMW",
    "MAHINDRA",
    "AUDI",
    "TATA",
    "MERCEDES",
    "FERRARI",
    "PORSCHE",
    "LUCKY",
    "FERRARI",
    "MERCEDES",
]


def get_cars():
    return CARS


def get_track_sequence():
    car_map = {car["key"]: car for car in CARS}
    return [car_map[key] for key in TRACK_SEQUENCE_KEYS]


def pick_winner():
    r = random.random()

    if r < 0.08:
        return next(car for car in CARS if car["key"] == "LUCKY")

    return random.choice([car for car in CARS if car["key"] != "LUCKY"])


def calculate_payout(bet_type: str, amount: float, winner: dict):
    if bet_type != winner["key"]:
        return 0.0

    return round(float(amount) * float(winner["payout"]), 2)