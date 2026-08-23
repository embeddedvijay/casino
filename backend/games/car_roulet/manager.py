import asyncio
import random
import uuid
from typing import Dict, List

from fastapi import WebSocket

from .engine import calculate_payout, get_cars, pick_winner


# Frontend के 20 equal-distance track positions के exact same order में।
TRACK_SEQUENCE_20 = [
    {"key": "bmw", "x": 50.00, "y": 9.00},
    {"key": "ferrari", "x": 64.28, "y": 9.29},
    {"key": "jaguar", "x": 78.16, "y": 12.31},
    {"key": "lamborghini", "x": 88.33, "y": 21.93},
    {"key": "land_rover", "x": 91.68, "y": 35.72},
    {"key": "maserati", "x": 92.00, "y": 50.00},
    {"key": "mercedes", "x": 91.68, "y": 64.28},
    {"key": "porsche", "x": 88.33, "y": 78.07},
    {"key": "bmw", "x": 78.16, "y": 87.69},
    {"key": "ferrari", "x": 64.28, "y": 90.71},
    {"key": "jaguar", "x": 50.00, "y": 91.00},
    {"key": "lamborghini", "x": 35.72, "y": 90.71},
    {"key": "land_rover", "x": 21.84, "y": 87.69},
    {"key": "maserati", "x": 11.67, "y": 78.07},
    {"key": "mercedes", "x": 8.32, "y": 64.28},
    {"key": "porsche", "x": 8.00, "y": 50.00},
    {"key": "bmw", "x": 8.32, "y": 35.72},
    {"key": "ferrari", "x": 11.67, "y": 21.93},
    {"key": "jaguar", "x": 21.84, "y": 12.31},
    {"key": "lamborghini", "x": 35.72, "y": 9.29},
]


WAITING_SECONDS = 10
RESULT_SECONDS = 5
STOPPING_SECONDS = 0.9
SPIN_LAPS = 3
FINAL_STOP_DELAYS = (
    0.700,
    0.900,
    1.100,
    1.400,
    1.800,
)

clients: List[WebSocket] = []


state = {
    "phase": "waiting",
    "round_id": "",
    "countdown": WAITING_SECONDS,
    "waiting_seconds": WAITING_SECONDS,
    "cars": get_cars(),
    "track": TRACK_SEQUENCE_20,
    "winner": None,
    "track_index": 0,
    "spin_progress": 0.0,
    "spin_delay_ms": 0,
    "spin_step": 0,
    "spin_total_steps": 0,
    "history": [],
}


bets_by_round: Dict[str, List[dict]] = {}
players_by_round: Dict[str, List[dict]] = {}
board_total_by_round: Dict[str, dict] = {}


BOT_NAMES = [
    "Raj Banna Saa",
    "player_OW2",
    "Raj Deepakvala",
    "Manish Halpati",
    "player_9RgLK",
    "player_EHvX1",
    "player_AK47",
    "player_RK21",
    "player_VIP9",
    "player_WIN7",
]


AVATARS = [
    "🧔",
    "👑",
    "👨",
    "🧑",
    "👨‍🦱",
    "👩",
    "🤖",
    "🎭",
    "🧑‍🚀",
    "👨‍✈️",
]


BET_AMOUNTS = [
    100,
    200,
    500,
    1000,
    1500,
    2000,
    3500,
    5000,
    7500,
    10000,
    20000,
    42569,
]


BOARD_TOTALS = [
    14640,
    20380,
    42100,
    41270,
    54880,
    45860,
    50220,
    65710,
]


def make_round_id():
    return "LR-" + str(uuid.uuid4())[:8].upper()


def generate_public_players():
    total = random.randint(8, 18)
    rows = []
    used_names = []

    for _ in range(total):
        name = random.choice(BOT_NAMES)

        if name in used_names:
            name = f"{name}_{random.randint(1, 99)}"

        used_names.append(name)

        rows.append(
            {
                "id": f"player-{uuid.uuid4()}",
                "name": name,
                "balance": float(random.choice(BET_AMOUNTS)),
                "avatar": random.choice(AVATARS),
                "tag": "",
            }
        )

    rows.sort(
        key=lambda item: item["balance"],
        reverse=True,
    )

    if rows:
        rows[0]["tag"] = "WINNER"

    if len(rows) > 1:
        rows[1]["tag"] = "LUCKY"

    return rows


def get_round_players(round_id=None):
    rid = round_id or state["round_id"]

    if not rid:
        return []

    if rid not in players_by_round:
        players_by_round[rid] = generate_public_players()

    return players_by_round[rid]


def get_round_board_totals(round_id=None):
    rid = round_id or state["round_id"]

    if not rid:
        return {}

    if rid not in board_total_by_round:
        board_total_by_round[rid] = {
            car["key"]: float(random.choice(BOARD_TOTALS))
            for car in state["cars"]
        }

    return board_total_by_round[rid]


def public_players():
    return get_round_players()


def board_totals():
    round_id = state["round_id"]
    static_totals = get_round_board_totals(round_id)
    totals = {}

    for car in state["cars"]:
        key = car["key"]

        totals[key] = {
            "my": 0.0,
            "total": float(static_totals.get(key, 0.0)),
        }

    for bet in bets_by_round.get(round_id, []):
        key = bet["bet_type"]

        if key in totals:
            totals[key]["my"] += float(bet["amount"])
            totals[key]["total"] += float(bet["amount"])

    return totals


def public_data():
    round_id = state["round_id"]

    return {
        "phase": state["phase"],
        "round_id": state["round_id"],
        "countdown": state["countdown"],
        "waiting_seconds": state["waiting_seconds"],
        "cars": state["cars"],
        "track": state["track"],
        "winner": state["winner"],
        "track_index": state["track_index"],
        "spin_progress": state["spin_progress"],
        "spin_delay_ms": state["spin_delay_ms"],
        "spin_step": state["spin_step"],
        "spin_total_steps": state["spin_total_steps"],
        "history": state["history"][-20:],
        "my_bets": bets_by_round.get(round_id, []),
        "board_totals": board_totals(),
        "players": get_round_players(round_id),
    }


async def broadcast(msg_type="state"):
    payload = {
        "type": msg_type,
        "data": public_data(),
    }

    dead = []

    for websocket in clients:
        try:
            await websocket.send_json(payload)
        except Exception:
            dead.append(websocket)

    for websocket in dead:
        if websocket in clients:
            clients.remove(websocket)


async def connect(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    await websocket.send_json(
        {
            "type": "state",
            "data": public_data(),
        }
    )


def disconnect(websocket: WebSocket):
    if websocket in clients:
        clients.remove(websocket)


async def place_bet(req):
    if state["phase"] != "betting":
        return {
            "success": False,
            "message": "Betting closed",
        }

    if req.amount <= 0:
        return {
            "success": False,
            "message": "Invalid amount",
        }

    valid_keys = [
        car["key"]
        for car in state["cars"]
    ]

    if req.bet_type not in valid_keys:
        return {
            "success": False,
            "message": "Invalid car option",
        }

    round_id = state["round_id"]
    round_bets = bets_by_round.setdefault(round_id, [])

    bet = {
        "id": "lr-bet-" + str(uuid.uuid4()),
        "user_id": req.user_id,
        "round_id": round_id,
        "bet_type": req.bet_type,
        "amount": float(req.amount),
        "status": "active",
        "payout": 0.0,
    }

    round_bets.append(bet)

    await broadcast("bet")

    return {
        "success": True,
        "message": "Bet placed",
    }


async def clear_bets(req):
    if state["phase"] != "betting":
        return {
            "success": False,
            "message": "Cannot clear now",
        }

    round_id = state["round_id"]
    old_bets = bets_by_round.get(round_id, [])

    bets_by_round[round_id] = [
        bet
        for bet in old_bets
        if bet["user_id"] != req.user_id
    ]

    await broadcast("clear")

    return {
        "success": True,
        "message": "Bets cleared",
    }


def settle_bets(winner):
    round_id = state["round_id"]

    for bet in bets_by_round.get(round_id, []):
        payout = calculate_payout(
            bet["bet_type"],
            bet["amount"],
            winner,
        )

        if payout > 0:
            bet["status"] = "won"
            bet["payout"] = payout
        else:
            bet["status"] = "lost"
            bet["payout"] = 0.0


def find_stop_index_for_winner(winner_key: str):
    track = state["track"]

    matching_indexes = [
        index
        for index, item in enumerate(track)
        if item.get("key") == winner_key
    ]

    if not matching_indexes:
        return 0

    return random.choice(matching_indexes)


def cleanup_old_rounds(keep=8):
    active_rounds = [
        state["round_id"]
    ] + [
        item.get("round_id")
        for item in state["history"][-keep:]
        if isinstance(item, dict)
    ]

    active_rounds = set(
        round_id
        for round_id in active_rounds
        if round_id
    )

    for store in (
        bets_by_round,
        players_by_round,
        board_total_by_round,
    ):
        for round_id in list(store.keys()):
            if round_id not in active_rounds:
                del store[round_id]


def spin_delay(progress: float) -> float:
    """Slow pickup, steady middle, gradual slowdown and a clear final stop."""
    progress = max(0.0, min(1.0, progress))

    # Start visibly and accelerate; Android WebView must render every index.
    if progress < 0.12:
        section = progress / 0.12
        return 0.180 - (section * 0.080)

    # Stable middle speed; never faster than 100 ms per position.
    if progress < 0.64:
        return 0.100

    # First slowdown stage.
    if progress < 0.84:
        section = (progress - 0.64) / 0.20
        return 0.100 + (section * 0.100)

    # Clearly visible slow movement near the result.
    if progress < 0.94:
        section = (progress - 0.84) / 0.10
        return 0.200 + (section * 0.180)

    # Last positions are deliberately very slow, with no sudden 1-second gap.
    section = (progress - 0.94) / 0.06
    return 0.380 + (section * 0.270)


async def game_loop():
    while True:
        round_id = make_round_id()

        state["phase"] = "betting"
        state["round_id"] = round_id
        state["countdown"] = WAITING_SECONDS
        state["waiting_seconds"] = WAITING_SECONDS
        state["winner"] = None
        state["spin_progress"] = 0.0
        state["spin_delay_ms"] = 0
        state["spin_step"] = 0
        state["spin_total_steps"] = 0

        bets_by_round[round_id] = []
        players_by_round[round_id] = generate_public_players()

        board_total_by_round[round_id] = {
            car["key"]: float(random.choice(BOARD_TOTALS))
            for car in state["cars"]
        }

        cleanup_old_rounds()

        for sec in range(
            WAITING_SECONDS,
            0,
            -1,
        ):
            state["phase"] = "betting"
            state["countdown"] = sec

            await broadcast(
                "new_round"
                if sec == WAITING_SECONDS
                else "countdown"
            )
            await asyncio.sleep(1)

        winner = pick_winner()
        stop_index = find_stop_index_for_winner(
            winner["key"]
        )

        state["phase"] = "spinning"
        state["countdown"] = 0
        state["winner"] = None
        state["spin_progress"] = 0.0
        state["spin_delay_ms"] = 120
        state["spin_step"] = 0

        await broadcast("spinning")
        await asyncio.sleep(0.12)

        track_len = len(state["track"])
        start_index = state["track_index"]
        distance_to_winner = (
            stop_index - start_index
        ) % track_len
        total_steps = (
            track_len * SPIN_LAPS
        ) + distance_to_winner
        state["spin_total_steps"] = total_steps

        for step in range(1, total_steps + 1):
            state["track_index"] = (
                start_index + step
            ) % track_len
            progress = step / max(
                total_steps,
                1,
            )
            delay = spin_delay(progress)
            remaining_steps = total_steps - step

            if remaining_steps < len(FINAL_STOP_DELAYS):
                delay_index = (
                    len(FINAL_STOP_DELAYS)
                    - 1
                    - remaining_steps
                )
                delay = FINAL_STOP_DELAYS[delay_index]

            state["spin_progress"] = round(progress, 4)
            state["spin_delay_ms"] = round(delay * 1000)
            state["spin_step"] = step

            await broadcast("spin_tick")
            await asyncio.sleep(delay)

        state["track_index"] = stop_index
        state["winner"] = winner
        state["phase"] = "stopping"
        state["spin_progress"] = 1.0
        state["spin_delay_ms"] = 0

        await broadcast("stop_effect")
        await asyncio.sleep(STOPPING_SECONDS)

        state["phase"] = "result"

        settle_bets(winner)

        state["history"].append(
            {
                "round_id": round_id,
                "winner": winner,
            }
        )

        if len(state["history"]) > 50:
            state["history"] = state["history"][-50:]

        await broadcast("result")
        await asyncio.sleep(RESULT_SECONDS)