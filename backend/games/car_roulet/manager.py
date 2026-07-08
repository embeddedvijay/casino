import asyncio
import random
import uuid
from typing import Dict, List
from fastapi import WebSocket
from .engine import calculate_payout, get_cars, pick_winner

TRACK_SEQUENCE_28=[
{"key":"bmw","x":27,"y":14},
{"key":"ferrari","x":36,"y":14},
{"key":"jaguar","x":45,"y":14},
{"key":"lamborghini","x":53,"y":14},
{"key":"land_rover","x":62,"y":14},
{"key":"maserati","x":70,"y":14},
{"key":"mercedes","x":80,"y":16},
{"key":"porsche","x":87,"y":23},
{"key":"bmw","x":91,"y":34},
{"key":"ferrari","x":91,"y":47},
{"key":"jaguar","x":91,"y":59},
{"key":"lamborghini","x":91,"y":71},
{"key":"land_rover","x":87,"y":82},
{"key":"maserati","x":80,"y":89},
{"key":"mercedes","x":71,"y":91},
{"key":"porsche","x":62,"y":91},
{"key":"bmw","x":53,"y":91},
{"key":"ferrari","x":44,"y":91},
{"key":"jaguar","x":35,"y":91},
{"key":"lamborghini","x":27,"y":91},
{"key":"land_rover","x":18,"y":89},
{"key":"maserati","x":12,"y":82},
{"key":"mercedes","x":8,"y":71},
{"key":"porsche","x":8,"y":59},
{"key":"bmw","x":8,"y":47},
{"key":"ferrari","x":8,"y":35},
{"key":"jaguar","x":12,"y":23},
{"key":"lamborghini","x":19,"y":16}
]

WAITING_SECONDS=10
RESULT_SECONDS=5
clients:List[WebSocket]=[]

state={
"phase":"waiting",
"round_id":"",
"countdown":WAITING_SECONDS,
"waiting_seconds":WAITING_SECONDS,
"cars":get_cars(),
"track":TRACK_SEQUENCE_28,
"winner":None,
"track_index":0,
"history":[]
}

bets_by_round:Dict[str,List[dict]]={}
players_by_round:Dict[str,List[dict]]={}
board_total_by_round:Dict[str,dict]={}

BOT_NAMES=["Raj Banna Saa","player_OW2","Raj Deepakvala","Manish Halpati","player_9RgLK","player_EHvX1","player_AK47","player_RK21","player_VIP9","player_WIN7"]
AVATARS=["🧔","👑","👨","🧑","👨‍🦱","👩","🤖","🎭","🧑‍🚀","👨‍✈️"]
BET_AMOUNTS=[100,200,500,1000,1500,2000,3500,5000,7500,10000,20000,42569]
BOARD_TOTALS=[14640,20380,42100,41270,54880,45860,50220,65710]


def make_round_id():
    return "LR-"+str(uuid.uuid4())[:8].upper()


def generate_public_players():
    total=random.randint(8,18)
    rows=[]
    used_names=[]
    for _ in range(total):
        name=random.choice(BOT_NAMES)
        if name in used_names:
            name=f"{name}_{random.randint(1,99)}"
        used_names.append(name)
        rows.append({
            "id":f"player-{uuid.uuid4()}",
            "name":name,
            "balance":float(random.choice(BET_AMOUNTS)),
            "avatar":random.choice(AVATARS),
            "tag":""
        })
    rows.sort(key=lambda x:x["balance"],reverse=True)
    if rows:
        rows[0]["tag"]="WINNER"
    if len(rows)>1:
        rows[1]["tag"]="LUCKY"
    return rows


def get_round_players(round_id=None):
    rid=round_id or state["round_id"]
    if not rid:
        return []
    if rid not in players_by_round:
        players_by_round[rid]=generate_public_players()
    return players_by_round[rid]


def get_round_board_totals(round_id=None):
    rid=round_id or state["round_id"]
    if not rid:
        return {}
    if rid not in board_total_by_round:
        board_total_by_round[rid]={car["key"]:float(random.choice(BOARD_TOTALS)) for car in state["cars"]}
    return board_total_by_round[rid]


def public_players():
    return get_round_players()


def board_totals():
    round_id=state["round_id"]
    static_totals=get_round_board_totals(round_id)
    totals={}
    for car in state["cars"]:
        key=car["key"]
        totals[key]={"my":0.0,"total":float(static_totals.get(key,0.0))}
    for bet in bets_by_round.get(round_id,[]):
        key=bet["bet_type"]
        if key in totals:
            totals[key]["my"]+=float(bet["amount"])
            totals[key]["total"]+=float(bet["amount"])
    return totals


def public_data():
    round_id=state["round_id"]
    return {
        "phase":state["phase"],
        "round_id":state["round_id"],
        "countdown":state["countdown"],
        "waiting_seconds":state["waiting_seconds"],
        "cars":state["cars"],
        "track":state["track"],
        "winner":state["winner"],
        "track_index":state["track_index"],
        "history":state["history"][-20:],
        "my_bets":bets_by_round.get(round_id,[]),
        "board_totals":board_totals(),
        "players":get_round_players(round_id)
    }


async def broadcast(msg_type="state"):
    payload={"type":msg_type,"data":public_data()}
    dead=[]
    for ws in clients:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in clients:
            clients.remove(ws)


async def connect(websocket:WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"type":"state","data":public_data()})


def disconnect(websocket:WebSocket):
    if websocket in clients:
        clients.remove(websocket)


async def place_bet(req):
    if state["phase"]!="betting":
        return {"success":False,"message":"Betting closed"}
    if req.amount<=0:
        return {"success":False,"message":"Invalid amount"}
    valid_keys=[car["key"] for car in state["cars"]]
    if req.bet_type not in valid_keys:
        return {"success":False,"message":"Invalid car option"}
    round_id=state["round_id"]
    round_bets=bets_by_round.setdefault(round_id,[])
    bet={"id":"lr-bet-"+str(uuid.uuid4()),"user_id":req.user_id,"round_id":round_id,"bet_type":req.bet_type,"amount":float(req.amount),"status":"active","payout":0.0}
    round_bets.append(bet)
    await broadcast("bet")
    return {"success":True,"message":"Bet placed"}


async def clear_bets(req):
    if state["phase"]!="betting":
        return {"success":False,"message":"Cannot clear now"}
    round_id=state["round_id"]
    old_bets=bets_by_round.get(round_id,[])
    bets_by_round[round_id]=[bet for bet in old_bets if bet["user_id"]!=req.user_id]
    await broadcast("clear")
    return {"success":True,"message":"Bets cleared"}


def settle_bets(winner):
    round_id=state["round_id"]
    for bet in bets_by_round.get(round_id,[]):
        payout=calculate_payout(bet["bet_type"],bet["amount"],winner)
        if payout>0:
            bet["status"]="won"
            bet["payout"]=payout
        else:
            bet["status"]="lost"
            bet["payout"]=0.0


def find_stop_index_for_winner(winner_key:str):
    track=state["track"]
    matching_indexes=[index for index,item in enumerate(track) if item.get("key")==winner_key]
    if not matching_indexes:
        return 0
    return random.choice(matching_indexes)


def cleanup_old_rounds(keep=8):
    active_rounds=[state["round_id"]]+[item.get("round_id") for item in state["history"][-keep:] if isinstance(item,dict)]
    active_rounds=set([r for r in active_rounds if r])
    for store in (bets_by_round,players_by_round,board_total_by_round):
        for rid in list(store.keys()):
            if rid not in active_rounds:
                del store[rid]


async def game_loop():
    while True:
        round_id=make_round_id()
        state["phase"]="betting"
        state["round_id"]=round_id
        state["countdown"]=WAITING_SECONDS
        state["waiting_seconds"]=WAITING_SECONDS
        state["winner"]=None
        state["track_index"]=0
        bets_by_round[round_id]=[]
        players_by_round[round_id]=generate_public_players()
        board_total_by_round[round_id]={car["key"]:float(random.choice(BOARD_TOTALS)) for car in state["cars"]}
        cleanup_old_rounds()
        await broadcast("new_round")

        for sec in range(WAITING_SECONDS,0,-1):
            state["phase"]="betting"
            state["countdown"]=sec
            await broadcast("countdown")
            await asyncio.sleep(1)

        winner=pick_winner()
        stop_index=find_stop_index_for_winner(winner["key"])
        state["phase"]="spinning"
        state["countdown"]=0
        state["winner"]=None
        await broadcast("spinning")

        track_len=len(state["track"])
        start_index=state["track_index"]
        total_steps=(track_len*3)+stop_index

        for step in range(total_steps+1):
            state["track_index"]=(start_index+step)%track_len
            await broadcast("spin_tick")
            progress=step/max(total_steps,1)
            delay=0.045+(progress**2)*0.16
            if progress>0.82:
                slow_progress=(progress-0.82)/0.18
                delay=0.22+slow_progress*0.18
            if progress>0.91:
                extra_slow_progress=(progress-0.91)/0.09
                delay=0.40+extra_slow_progress*0.30
            if progress>0.95:
                delay=0.85
            if progress>0.98:
                delay=0.95
            await asyncio.sleep(delay)

        state["track_index"]=stop_index
        state["winner"]=winner
        state["phase"]="stopping"
        await broadcast("stop_effect")
        await asyncio.sleep(1.2)

        state["phase"]="result"
        settle_bets(winner)
        state["history"].append({"round_id":round_id,"winner":winner})
        if len(state["history"])>50:
            state["history"]=state["history"][-50:]
        await broadcast("result")
        await asyncio.sleep(RESULT_SECONDS)