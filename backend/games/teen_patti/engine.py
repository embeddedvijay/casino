import random
import secrets


SUITS = ("♠", "♥", "♦", "♣")


def shuffled_deck():
    deck = [
        {"id": f"{rank}-{suit}", "rank": rank, "suit": suit, "red": suit in {"♥", "♦"}}
        for suit in SUITS
        for rank in range(2, 15)
    ]
    secrets.SystemRandom().shuffle(deck)
    return deck


def evaluate(cards):
    ranks = sorted((int(card["rank"]) for card in cards), reverse=True)
    flush = len({card["suit"] for card in cards}) == 1
    unique = sorted(set(ranks), reverse=True)
    straight_high = None
    if unique == [14, 3, 2]:
        straight_high = 3
    elif len(unique) == 3 and unique[0] - unique[2] == 2:
        straight_high = unique[0]
    counts = sorted(((ranks.count(rank), rank) for rank in set(ranks)), reverse=True)
    if len(unique) == 1:
        return (6, ranks[0]), "TRAIL"
    if straight_high and flush:
        return (5, straight_high), "PURE SEQUENCE"
    if straight_high:
        return (4, straight_high), "SEQUENCE"
    if flush:
        return (3, *ranks), "COLOR"
    if counts[0][0] == 2:
        pair = counts[0][1]
        kicker = next(rank for rank in ranks if rank != pair)
        return (2, pair, kicker), "PAIR"
    return (1, *ranks), "HIGH CARD"


def choose_auto_action(cards, chaals):
    score, _ = evaluate(cards)
    if chaals > 0 and score[0] == 1 and score[1] < 11 and random.random() < 0.58:
        return "pack"
    return "chaal"


def winner_keys(hands, active):
    players = [key for key in ("user", "auto1", "auto2") if active.get(key)]
    best = max(evaluate(hands[key])[0] for key in players)
    return [key for key in players if evaluate(hands[key])[0] == best]


def random_alias():
    return f"Guest {secrets.randbelow(9000) + 1000}"

