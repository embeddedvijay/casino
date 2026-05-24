from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import random
import uuid
import time

app = FastAPI(title="Aviator Style Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []

state = {
    "round_id": "WAITING",
    "phase": "waiting",
    "multiplier": 1.0,
    "countdown": 3,
    "crashed_at": None,
    "server_time": time.time(),
}

history: List[float] = [1.14, 1.26, 7.77, 2.27, 1.16, 4.48, 1.55, 2.22, 97.22, 2.65, 5.26, 14.63]

players = [
    "c***0", "c***0", "9***4", "r***3", "2***3", "9***4", "r***3", "9***c",
    "r***5", "d***8", "s***6", "9***1", "r***4", "r***3", "r***0", "r***2"
]

avatars = ["👨🏻‍🚀", "🧑", "🤡", "🦊", "👩", "🧑‍💼", "👨‍🚒", "🤖", "🧙", "🧑‍🎤", "🛡️", "🎧", "🎭", "🧑‍✈️", "🌸", "👑"]

all_bets = []
for i, name in enumerate(players):
    bet = random.choice([500, 520, 550, 600, 800, 850, 1000, 1600, 1855, 3550, 4550])
    all_bets.append({
        "id": str(uuid.uuid4()),
        "user": name,
        "avatar": avatars[i % len(avatars)],
        "bet": float(bet),
        "cashout": 0.0,
    })

user_bets: Dict[str, dict] = {}

class BetRequest(BaseModel):
    user_id: str = "demo_user"
    amount: float
    seat: int = 1

class CashoutRequest(BaseModel):
    user_id: str = "demo_user"
    seat: int = 1


def public_state():
    return {
        **state,
        "history": history[:24],
        "all_bets": all_bets[:40],
        "my_bets": list(user_bets.values()),
    }

async def broadcast(payload: dict):
    disconnected = []
    for ws in list(clients):
        try:
            await ws.send_json(payload)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in clients:
            clients.remove(ws)

@app.websocket("/ws/game")
async def ws_game(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"type": "snapshot", "data": public_state()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)

@app.get("/api/state")
async def get_state():
    return public_state()

@app.post("/api/bet")
async def place_bet(req: BetRequest):
    if state["phase"] != "betting":
        return {"success": False, "message": "Betting closed"}
    if req.amount <= 0:
        return {"success": False, "message": "Invalid amount"}
    key = f"{req.user_id}:{req.seat}:{state['round_id']}"
    if key in user_bets:
        return {"success": False, "message": "Bet already placed"}

    bet = {
        "id": key,
        "round_id": state["round_id"],
        "seat": req.seat,
        "amount": round(req.amount, 2),
        "status": "active",
        "cashout_multiplier": None,
        "cashout_amount": 0.0,
    }
    user_bets[key] = bet
    await broadcast({"type": "my_bets", "data": list(user_bets.values())})
    return {"success": True, "message": "Bet placed", "bet": bet}

@app.post("/api/cashout")
async def cashout(req: CashoutRequest):
    if state["phase"] != "flying":
        return {"success": False, "message": "Cashout not available"}

    matched: Optional[str] = None
    for key, bet in user_bets.items():
        if key.startswith(f"{req.user_id}:{req.seat}:") and bet["round_id"] == state["round_id"] and bet["status"] == "active":
            matched = key
            break
    if not matched:
        return {"success": False, "message": "No active bet"}

    bet = user_bets[matched]
    bet["status"] = "cashed_out"
    bet["cashout_multiplier"] = round(float(state["multiplier"]), 2)
    bet["cashout_amount"] = round(bet["amount"] * bet["cashout_multiplier"], 2)
    await broadcast({"type": "my_bets", "data": list(user_bets.values())})
    return {"success": True, "message": "Cashed out", "bet": bet}


def next_crash_point():
    roll = random.random()
    if roll < 0.70:
        return round(random.uniform(1.05, 2.30), 2)
    if roll < 0.92:
        return round(random.uniform(2.31, 8.0), 2)
    if roll < 0.985:
        return round(random.uniform(8.01, 35.0), 2)
    return round(random.uniform(35.01, 120.0), 2)


def refresh_fake_bets():
    global all_bets
    rows = []
    for i, name in enumerate(players):
        bet = random.choice([100, 200, 500, 520, 550, 600, 800, 850, 1000, 1600, 1855, 3550, 4550])
        rows.append({
            "id": str(uuid.uuid4()),
            "user": name,
            "avatar": avatars[i % len(avatars)],
            "bet": float(bet),
            "cashout": 0.0,
        })
    all_bets = sorted(rows, key=lambda x: x["bet"], reverse=True)

@app.on_event("startup")
async def start_loop():
    asyncio.create_task(game_loop())

async def game_loop():
    global state, history
    while True:
        refresh_fake_bets()
        round_id = str(uuid.uuid4())
        display_round = f"{round_id[:8]}-{round_id[9:13]}-{round_id[14:18]}-{round_id[19:23]}-{round_id[24:]}"
        state = {
            "round_id": display_round,
            "phase": "betting",
            "multiplier": 1.0,
            "countdown": 5,
            "crashed_at": None,
            "server_time": time.time(),
        }
        await broadcast({"type": "snapshot", "data": public_state()})

        for sec in range(5, 0, -1):
            state["countdown"] = sec
            state["server_time"] = time.time()
            await broadcast({"type": "tick", "data": public_state()})
            await asyncio.sleep(1)

        crash_at = next_crash_point()
        state["phase"] = "flying"
        state["multiplier"] = 1.0
        state["crashed_at"] = None
        await broadcast({"type": "tick", "data": public_state()})

        multiplier = 1.0
        while multiplier < crash_at:
            await asyncio.sleep(0.08)
            multiplier = round(multiplier + (0.01 + multiplier * 0.006), 2)
            state["multiplier"] = multiplier
            state["server_time"] = time.time()
            await broadcast({"type": "tick", "data": public_state()})

        state["phase"] = "crashed"
        state["multiplier"] = crash_at
        state["crashed_at"] = crash_at
        history = [crash_at] + history[:23]
        for bet in user_bets.values():
            if bet["round_id"] == state["round_id"] and bet["status"] == "active":
                bet["status"] = "lost"
        await broadcast({"type": "crash", "data": public_state()})
        await asyncio.sleep(4)
