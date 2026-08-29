import asyncio
import random
import time
import uuid
from typing import Dict, List
from fastapi import WebSocket
from .engine import calculate_cashout, calculate_multiplier, generate_crash_point
from core.casino import CasinoError, close_round, open_round, place_bet as persist_bet, settle_bet

WAITING_SECONDS = 10
clients: List[WebSocket] = []

state = {"phase":"waiting","round_id":"","multiplier":1.0,"countdown":WAITING_SECONDS,"waiting_seconds":WAITING_SECONDS,"crashed_at":None,"history":[]}
bets_by_round: Dict[str, List[dict]] = {}
bot_bets_by_round: Dict[str, List[dict]] = {}

def make_round_id():
    return str(uuid.uuid4())

def random_user():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return f"{random.choice(letters)}***{random.randint(0,9)}"

def random_avatar():
    return random.choice(["👨‍✈️","🧑","👩","🤖","🎭","👨","🧔","👳","🧑‍🚀","🧑‍🎤"])

def now_time():
    return time.strftime("%H:%M:%S")

def generate_bot_bets():
    total=random.randint(18,40)
    rows=[]
    for _ in range(total):
        amount=random.choice([1000,20000,1300,3500,4000,500,100,1200,1500,2000,7500,8700,12000,1050,22000,150,5500,8000,2500,2100,3200,4500,6000,9500,700,2000])
        rows.append({"id":f"bot-{uuid.uuid4()}","avatar":random_avatar(),"user":random_user(),"bet":float(amount),"cashout":0.0,"cashout_multiplier":None,"cashout_time":None})
    return rows

def public_data():
    round_id=state["round_id"]
    all_bets=list(bot_bets_by_round.get(round_id,[]))
    for bet in bets_by_round.get(round_id,[]):
        all_bets.insert(0,{"id":bet["id"],"avatar":"🟢","user":"You","bet":bet["amount"],"cashout":bet.get("cashout_amount",0.0),"cashout_multiplier":bet.get("cashout_multiplier"),"cashout_time":bet.get("cashout_time"),"status":bet.get("status")})
    return {"phase":state["phase"],"round_id":state["round_id"],"multiplier":state["multiplier"],"countdown":state["countdown"],"waiting_seconds":state["waiting_seconds"],"crashed_at":state["crashed_at"],"history":state["history"][-25:],"all_bets":all_bets,"my_bets":bets_by_round.get(round_id,[])}

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

async def connect(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"type":"state","data":public_data()})

def disconnect(websocket: WebSocket):
    if websocket in clients:
        clients.remove(websocket)

async def place_bet(req):
    if state["phase"]!="betting":
        return {"success":False,"message":"Betting closed"}
    if req.amount<=0:
        return {"success":False,"message":"Invalid amount"}
    if req.seat not in [1,2]:
        return {"success":False,"message":"Invalid seat"}
    round_id=state["round_id"]
    round_bets=bets_by_round.setdefault(round_id,[])
    old=next((bet for bet in round_bets if bet["user_id"]==req.user_id and bet["seat"]==req.seat),None)
    if old:
        return {"success":False,"message":"Bet already placed"}
    try:
        saved=persist_bet(game="aviator",round_id=round_id,user_id=req.user_id,amount=req.amount,position_key=f"seat:{req.seat}",metadata={"seat":req.seat})
    except CasinoError as exc:
        return {"success":False,"message":str(exc),"code":exc.code}
    bet={"id":saved["id"],"user_id":req.user_id,"seat":req.seat,"round_id":round_id,"amount":float(req.amount),"status":"active","cashout_multiplier":None,"cashout_amount":0.0,"cashout_time":None,"balance":saved["balance"]}
    round_bets.append(bet)
    await broadcast("bet")
    return {"success":True,"message":"Bet accepted","bet_id":bet["id"],"balance":saved["balance"]}

async def cashout(req):
    if state["phase"]!="flying":
        return {"success":False,"message":"Cashout not available"}
    round_id=state["round_id"]
    round_bets=bets_by_round.get(round_id,[])
    bet=next((item for item in round_bets if item["user_id"]==req.user_id and item["seat"]==req.seat and item["status"]=="active"),None)
    if not bet:
        return {"success":False,"message":"No active bet"}
    multiplier=round(float(state["multiplier"]),2)
    win_amount=calculate_cashout(bet["amount"],multiplier)
    bet["status"]="cashed_out"
    bet["cashout_multiplier"]=multiplier
    bet["cashout_amount"]=win_amount
    bet["cashout_time"]=now_time()
    settled=settle_bet(bet["id"],win_amount,{"multiplier":multiplier})
    for row in bot_bets_by_round.get(round_id,[]):
        if random.random()<0.12 and row["cashout"]==0:
            row["cashout_multiplier"]=multiplier
            row["cashout"]=round(row["bet"]*multiplier,2)
            row["cashout_time"]=now_time()
    await broadcast("cashout")
    return {"success":True,"message":f"Cashout {multiplier}x","cashout_multiplier":multiplier,"cashout_amount":win_amount,"cashout_time":bet["cashout_time"],"balance":settled.get("balance") if settled else None}

async def game_loop():
    while True:
        round_id=make_round_id()
        state["phase"]="betting"
        state["round_id"]=round_id
        state["multiplier"]=1.0
        state["countdown"]=WAITING_SECONDS
        state["waiting_seconds"]=WAITING_SECONDS
        state["crashed_at"]=None
        bets_by_round[round_id]=[]
        bot_bets_by_round[round_id]=generate_bot_bets()
        open_round("aviator",round_id,{"phase":"betting"})
        await broadcast("new_round")
        for sec in range(WAITING_SECONDS,0,-1):
            state["phase"]="betting"
            state["countdown"]=sec
            state["multiplier"]=1.0
            await broadcast("countdown")
            await asyncio.sleep(1)
        crash_point=generate_crash_point()
        state["phase"]="flying"
        state["countdown"]=0
        state["multiplier"]=1.0
        await broadcast("started")
        start_time=time.time()
        while True:
            elapsed=time.time()-start_time
            multiplier=round(calculate_multiplier(elapsed),2)
            if multiplier>=crash_point:
                break
            state["multiplier"]=multiplier
            for row in bot_bets_by_round.get(round_id,[]):
                if row["cashout"]==0:
                    auto_cashout_at=random.choice([1.25,1.35,1.50,1.75,2.0,2.5,3.0,4.0])
                    if multiplier>=auto_cashout_at and random.random()<0.04:
                        row["cashout_multiplier"]=multiplier
                        row["cashout"]=round(row["bet"]*multiplier,2)
                        row["cashout_time"]=now_time()
            await broadcast("tick")
            await asyncio.sleep(0.06)
        state["phase"]="crashed"
        state["multiplier"]=crash_point
        state["crashed_at"]=crash_point
        state["history"].append(crash_point)
        if len(state["history"])>60:
            state["history"]=state["history"][-60:]
        for bet in bets_by_round.get(round_id,[]):
            if bet["status"]=="active":
                bet["status"]="lost"
                settle_bet(bet["id"],0.0,{"crashed_at":crash_point})
        close_round("aviator",round_id,{"crashed_at":crash_point})
        await broadcast("crashed")
        await asyncio.sleep(5)
