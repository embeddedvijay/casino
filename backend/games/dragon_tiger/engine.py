import random


RANKS = [
    {"label": "A", "value": 1},
    {"label": "2", "value": 2},
    {"label": "3", "value": 3},
    {"label": "4", "value": 4},
    {"label": "5", "value": 5},
    {"label": "6", "value": 6},
    {"label": "7", "value": 7},
    {"label": "8", "value": 8},
    {"label": "9", "value": 9},
    {"label": "10", "value": 10},
    {"label": "J", "value": 11},
    {"label": "Q", "value": 12},
    {"label": "K", "value": 13},
]

SUITS = [
    {"label": "HEART", "symbol": "♥", "color": "red"},
    {"label": "DIAMOND", "symbol": "♦", "color": "red"},
    {"label": "CLUB", "symbol": "♣", "color": "black"},
    {"label": "SPADE", "symbol": "♠", "color": "black"},
]


def draw_card():
    rank = random.choice(RANKS)
    suit = random.choice(SUITS)

    return {
        "rank": rank["label"],
        "value": rank["value"],
        "suit": suit["label"],
        "symbol": suit["symbol"],
        "color": suit["color"],
    }


def get_size(value: int):
    return "SMALL" if value <= 6 else "BIG"


def get_odd_even(value: int):
    return "ODD" if value % 2 else "EVEN"


def calculate_result(dragon_card: dict, tiger_card: dict):
    if dragon_card["value"] > tiger_card["value"]:
        winner = "DRAGON"
    elif tiger_card["value"] > dragon_card["value"]:
        winner = "TIGER"
    else:
        winner = "TIE"

    suited_tie = (
        dragon_card["value"] == tiger_card["value"]
        and dragon_card["suit"] == tiger_card["suit"]
    )

    result = {
        "winner": winner,
        "suited_tie": suited_tie,
        "dragon_size": get_size(dragon_card["value"]),
        "tiger_size": get_size(tiger_card["value"]),
        "dragon_odd_even": get_odd_even(dragon_card["value"]),
        "tiger_odd_even": get_odd_even(tiger_card["value"]),
        "dragon_suit": dragon_card["suit"],
        "tiger_suit": tiger_card["suit"],
    }

    return result


def is_winning_bet(bet_type: str, result: dict):
    if bet_type == "DRAGON":
        return result["winner"] == "DRAGON"

    if bet_type == "TIGER":
        return result["winner"] == "TIGER"

    if bet_type == "TIE":
        return result["winner"] == "TIE"

    if bet_type == "SUITED_TIE":
        return result["suited_tie"]

    if bet_type == "DRAGON_BIG":
        return result["dragon_size"] == "BIG"

    if bet_type == "DRAGON_SMALL":
        return result["dragon_size"] == "SMALL"

    if bet_type == "DRAGON_ODD":
        return result["dragon_odd_even"] == "ODD"

    if bet_type == "DRAGON_EVEN":
        return result["dragon_odd_even"] == "EVEN"

    if bet_type == "TIGER_BIG":
        return result["tiger_size"] == "BIG"

    if bet_type == "TIGER_SMALL":
        return result["tiger_size"] == "SMALL"

    if bet_type == "TIGER_ODD":
        return result["tiger_odd_even"] == "ODD"

    if bet_type == "TIGER_EVEN":
        return result["tiger_odd_even"] == "EVEN"

    if bet_type.startswith("DRAGON_"):
        suit = bet_type.replace("DRAGON_", "")
        return result["dragon_suit"] == suit

    if bet_type.startswith("TIGER_"):
        suit = bet_type.replace("TIGER_", "")
        return result["tiger_suit"] == suit

    return False


def get_payout_multiplier(bet_type: str):
    if bet_type in ["DRAGON", "TIGER"]:
        return 1.95

    if bet_type == "TIE":
        return 8

    if bet_type == "SUITED_TIE":
        return 50

    if bet_type.endswith("_BIG") or bet_type.endswith("_SMALL"):
        return 1.9

    if bet_type.endswith("_ODD") or bet_type.endswith("_EVEN"):
        return 1.9

    if bet_type.endswith("_HEART"):
        return 3.8

    if bet_type.endswith("_DIAMOND"):
        return 3.8

    if bet_type.endswith("_CLUB"):
        return 3.8

    if bet_type.endswith("_SPADE"):
        return 3.8

    return 1