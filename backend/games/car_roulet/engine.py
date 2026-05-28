import random

CARS = [
    {"key": "bmw", "label": "BMW", "payout": 6},
    {"key": "ferrari", "label": "FERRARI", "payout": 6},
    {"key": "jaguar", "label": "JAGUAR", "payout": 6},
    {"key": "lamborghini", "label": "LAMBORGHINI", "payout": 6},
    {"key": "land_rover", "label": "LAND ROVER", "payout": 6},
    {"key": "maserati", "label": "MASERATI", "payout": 6},
    {"key": "mercedes", "label": "MERCEDES", "payout": 6},
    {"key": "porsche", "label": "PORSCHE", "payout": 6},
    {"key": "star", "label": "STAR", "payout": 12},
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
    r = random.random()
    if r < 0.06:
        return next(car for car in CARS if car["key"] == "star")
    return random.choice([car for car in CARS if car["key"] != "star"])

def calculate_payout(bet_type: str, amount: float, winner: dict):
    if bet_type != winner["key"]:
        return 0.0
    return round(float(amount) * float(winner["payout"]), 2)