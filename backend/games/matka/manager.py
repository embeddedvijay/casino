import asyncio
import random
import uuid
from typing import Dict, List

from fastapi import WebSocket
from core.casino import CasinoError, cancel_user_bets, close_round, open_round, place_bet as persist_bet, settle_bet

from .engine import calculate_payout, get_numbers, pick_winner


WAITING_SECONDS = 10
RESULT_SECONDS = 5

clients: List[WebSocket] = []

state = {
    "phase": "waiting",
    "round_id": "",
    "countdown": WAITING_SECONDS,
    "waiting_seconds": WAITING_SECONDS,
    "numbers": get_numbers(),
    "winner": None,
    "history": [],
}

bets_by_round: Dict[str, List[dict]] = {}


def make_round_id():
    return "MTK-" + str(uuid.uuid4())[:8].upper()


def board_totals():
    round_id = state["round_id"]

    totals = {
        item["key"]: {
            "my": 0.0,
            "total": random.choice([1200, 2500, 3800, 5200, 7600]),
        }
        for item in state["numbers"]
    }

    for bet in bets_by_round.get(round_id, []):
        key = bet["bet_type"]
        if key in totals:
            totals[key]["my"] += float(bet["amount"])

    return totals


def public_players():
    return [
        {"name": "player_1", "balance": 1200, "avatar": "👤", "tag": ""},
        {"name": "player_2", "balance": 2500, "avatar": "👑", "tag": ""},
        {"name": "player_3", "balance": 800, "avatar": "🙂", "tag": ""},
    ]


def public_data():
    round_id = state["round_id"]

    return {
        "phase": state["phase"],
        "round_id": state["round_id"],
        "countdown": state["countdown"],
        "waiting_seconds": state["waiting_seconds"],
        "numbers": state["numbers"],
        "winner": state["winner"],
        "history": state["history"][-20:],
        "my_bets": bets_by_round.get(round_id, []),
        "board_totals": board_totals(),
        "players": public_players(),
    }


async def broadcast(msg_type="state"):
    payload = {
        "type": msg_type,
        "data": public_data(),
    }

    dead = []

    for ws in clients:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)

    for ws in dead:
        if ws in clients:
            clients.remove(ws)


async def connect(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    await websocket.send_json({
        "type": "state",
        "data": public_data(),
    })


def disconnect(websocket: WebSocket):
    if websocket in clients:
        clients.remove(websocket)


async def place_bet(req):
    if state["phase"] != "betting":
        return {"success": False, "message": "Betting closed"}

    if req.amount <= 0:
        return {"success": False, "message": "Invalid amount"}

    valid_keys = [item["key"] for item in state["numbers"]]

    if req.bet_type not in valid_keys:
        return {"success": False, "message": "Invalid number"}

    round_id = state["round_id"]
    round_bets = bets_by_round.setdefault(round_id, [])

    try:
        saved=persist_bet(game="matka",round_id=round_id,user_id=req.user_id,amount=req.amount,position_key=str(req.bet_type),metadata={"bet_type":req.bet_type},client_id=req.client_id)
    except CasinoError as exc:
        return {"success":False,"message":str(exc),"code":exc.code}
    bet = {
        "id": saved["id"],
        "client_id": req.client_id,
        "user_id": req.user_id,
        "round_id": round_id,
        "bet_type": req.bet_type,
        "amount": float(req.amount),
        "status": "active",
        "payout": 0.0,
    }

    round_bets.append(bet)

    await broadcast("bet")

    return {"success": True, "message": "Bet placed", "bet_id":bet["id"], "balance":saved["balance"]}


async def clear_bets(req):
    if state["phase"] != "betting":
        return {"success": False, "message": "Cannot clear now"}

    round_id = state["round_id"]
    old_bets = bets_by_round.get(round_id, [])
    cancel_user_bets("matka",round_id,req.user_id,req.client_id)

    bets_by_round[round_id] = [
        bet for bet in old_bets if not (bet.get("client_id","demo") == req.client_id and bet["user_id"] == req.user_id)
    ]

    await broadcast("clear")

    return {"success": True, "message": "Bets cleared"}


def settle_bets(winner):
    round_id = state["round_id"]

    for bet in bets_by_round.get(round_id, []):
        payout = calculate_payout(bet["bet_type"], bet["amount"], winner)

        if payout > 0:
            bet["status"] = "won"
            bet["payout"] = payout
        else:
            bet["status"] = "lost"
            bet["payout"] = 0.0
        settle_bet(bet["id"],bet["payout"],winner)


async def game_loop():
    while True:
        round_id = make_round_id()

        state["phase"] = "betting"
        state["round_id"] = round_id
        state["countdown"] = WAITING_SECONDS
        state["winner"] = None
        bets_by_round[round_id] = []
        open_round("matka",round_id,{"phase":"betting"})

        await broadcast("new_round")

        for sec in range(WAITING_SECONDS, 0, -1):
            state["phase"] = "betting"
            state["countdown"] = sec
            await broadcast("countdown")
            await asyncio.sleep(1)

        state["phase"] = "result"
        state["countdown"] = 0

        winner = pick_winner()
        state["winner"] = winner

        settle_bets(winner)
        close_round("matka",round_id,winner)

        state["history"].append({
            "round_id": round_id,
            "winner": winner,
        })

        state["history"] = state["history"][-50:]

        await broadcast("result")

        await asyncio.sleep(RESULT_SECONDS)
