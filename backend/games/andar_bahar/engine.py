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


def create_round():
    deck = shuffled_deck()
    joker = deck.pop()
    return joker, deck


def deal_round(joker, deck):
    deck = list(deck)
    deals = []
    side = "andar"
    winner = None
    while deck:
        card = deck.pop()
        deals.append({"side": side, "card": card})
        if card["rank"] == joker["rank"]:
            winner = side
            break
        side = "bahar" if side == "andar" else "andar"
    return joker, deals, winner
