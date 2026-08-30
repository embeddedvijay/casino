import random

CARS = [
    {"key": "bmw", "label": "BMW", "payout": 5},
    {"key": "ferrari", "label": "FERRARI", "payout": 8},
    {"key": "jaguar", "label": "JAGUAR", "payout": 5},
    {"key": "lamborghini", "label": "LAMBORGHINI", "payout": 8},
    {"key": "land_rover", "label": "LAND ROVER", "payout": 5},
    {"key": "maserati", "label": "MASERATI", "payout": 8},
    {"key": "mercedes", "label": "MERCEDES", "payout": 5},
    {"key": "porsche", "label": "PORSCHE", "payout": 8},
]

TRACK_SEQUENCE_KEYS = [
    "bmw", "ferrari", "jaguar", "lamborghini", "land_rover", "maserati",
    "star", "mercedes", "porsche", "bmw", "ferrari", "jaguar",
    "lamborghini", "land_rover", "maserati", "mercedes", "porsche",
    "bmw", "ferrari", "jaguar", "lamborghini", "land_rover", "maserati",
    "mercedes", "porsche", "bmw", "ferrari", "jaguar", "lamborghini",
    "land_rover", "maserati", "mercedes", "porsche", "bmw", "ferrari",
    "jaguar", "lamborghini", "land_rover",
]

def get_cars():
    return CARS

def get_track_sequence():
    car_map = {car["key"]: car for car in CARS}
    return [car_map[key] for key in TRACK_SEQUENCE_KEYS]

def pick_winner():
    weights = [1] * len(CARS)
    return random.choices(CARS, weights=weights, k=1)[0]

def calculate_payout(bet_type: str, amount: float, winner: dict):
    if bet_type != winner["key"]:
        return 0.0
    return round(float(amount) * float(winner["payout"]), 2)