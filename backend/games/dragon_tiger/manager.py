import asyncio
import random
import uuid
from typing import Dict, List

from fastapi import WebSocket

from .engine import (
    calculate_result,
    draw_card,
    get_payout_multiplier,
    is_winning_bet,
)
from core.casino import CasinoError, cancel_user_bets, close_round, open_round, place_bet as persist_bet, settle_bet


WAITING_SECONDS = 15
DEALING_SECONDS = 3
RESULT_SECONDS = 5

clients: List[WebSocket] = []

state = {
    "phase": "waiting",  # betting / dealing / result
    "round_id": "",
    "countdown": WAITING_SECONDS,
    "waiting_seconds": WAITING_SECONDS,
    "dragon_card": None,
    "tiger_card": None,
    "result": None,
    "history": [],
}

bets_by_round: Dict[str, List[dict]] = {}


def make_round_id():
    return "DT-" + str(uuid.uuid4())[:8].upper()


def public_data():
    round_id = state["round_id"]

    return {
        "phase": state["phase"],
        "round_id": state["round_id"],
        "countdown": state["countdown"],
        "waiting_seconds": state["waiting_seconds"],
        "dragon_card": state["dragon_card"],
        "tiger_card": state["tiger_card"],
        "result": state["result"],
        "history": state["history"][-80:],
        "my_bets": bets_by_round.get(round_id, []),
        "total_bet": sum(float(b["amount"]) for b in bets_by_round.get(round_id, [])),
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
        return {
            "success": False,
            "message": "Betting closed",
        }

    if req.amount <= 0:
        return {
            "success": False,
            "message": "Invalid amount",
        }

    round_id = state["round_id"]
    round_bets = bets_by_round.setdefault(round_id, [])

    try:
        # Every tap is a separate wager. A unique position key prevents the
        # persistence layer's duplicate-bet guard from blocking repeat bets on
        # the same Dragon/Tiger option during the open betting window.
        bet_key=f"{req.bet_type}:{uuid.uuid4()}"
        saved=persist_bet(game="dragon-tiger",round_id=round_id,user_id=req.user_id,amount=req.amount,position_key=bet_key,metadata={"bet_type":req.bet_type})
    except CasinoError as exc:
        return {"success":False,"message":str(exc),"code":exc.code}
    bet = {
        "id": saved["id"],
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
        "bet_id": bet["id"],
        "balance": saved["balance"],
    }


async def clear_bets(req):
    if state["phase"] != "betting":
        return {
            "success": False,
            "message": "Cannot clear now",
        }

    round_id = state["round_id"]
    old = bets_by_round.get(round_id, [])
    cancel_user_bets("dragon-tiger",round_id,req.user_id)

    bets_by_round[round_id] = [
        b for b in old if b["user_id"] != req.user_id
    ]

    await broadcast("clear")

    return {
        "success": True,
        "message": "Bets cleared",
    }


def settle_bets(result):
    round_id = state["round_id"]

    for bet in bets_by_round.get(round_id, []):
        if is_winning_bet(bet["bet_type"], result):
            multiplier = get_payout_multiplier(bet["bet_type"])
            bet["status"] = "won"
            bet["payout"] = round(bet["amount"] * multiplier, 2)
        else:
            bet["status"] = "lost"
            bet["payout"] = 0.0
        settle_bet(bet["id"],bet["payout"],result)


async def game_loop():
    while True:
        round_id = make_round_id()

        state["phase"] = "betting"
        state["round_id"] = round_id
        state["countdown"] = WAITING_SECONDS
        state["waiting_seconds"] = WAITING_SECONDS
        state["dragon_card"] = None
        state["tiger_card"] = None
        state["result"] = None

        bets_by_round[round_id] = []
        open_round("dragon-tiger",round_id,{"phase":"betting"})

        await broadcast("new_round")

        for sec in range(WAITING_SECONDS, 0, -1):
            state["phase"] = "betting"
            state["countdown"] = sec

            await broadcast("countdown")
            await asyncio.sleep(1)

        state["phase"] = "dealing"
        state["countdown"] = 0
        state["dragon_card"] = None
        state["tiger_card"] = None
        state["result"] = None

        await broadcast("dealing")
        await asyncio.sleep(1)

        dragon_card = draw_card()
        state["dragon_card"] = dragon_card

        await broadcast("dragon_reveal")
        await asyncio.sleep(1)

        tiger_card = draw_card()
        state["tiger_card"] = tiger_card

        await broadcast("tiger_reveal")
        await asyncio.sleep(1)

        result = calculate_result(dragon_card, tiger_card)
        state["phase"] = "result"
        state["result"] = result

        settle_bets(result)
        close_round("dragon-tiger",round_id,result)

        state["history"].append({
            "round_id": round_id,
            "winner": result["winner"],
            "suited_tie": result["suited_tie"],
            "dragon": dragon_card,
            "tiger": tiger_card,
        })

        if len(state["history"]) > 100:
            state["history"] = state["history"][-100:]

        await broadcast("result")

        await asyncio.sleep(RESULT_SECONDS)
