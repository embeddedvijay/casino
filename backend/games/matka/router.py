import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pymongo import MongoClient
from bson import ObjectId
from . import manager
from .schemas import MatkaBetRequest, MatkaClearRequest, MarketMessageRequest
from pydantic import BaseModel
from hla_adv import adv_run as h

router=APIRouter(prefix="/api/games/matka",tags=["Matka"])

MONGO_URL="mongodb://localhost:27017"
mongo_client=MongoClient(MONGO_URL)
market_db=mongo_client["Market"]

BOARD_RESET_TIME=datetime.time(1,0,0)

def get_result_collection():
    current_date_time=datetime.datetime.now()
    if current_date_time.time()<BOARD_RESET_TIME:
        date=current_date_time-datetime.timedelta(days=1)
    else:
        date=current_date_time
    collection_name=date.strftime("%y-%m-%d")
    return market_db[collection_name]

def mongo_to_json(data):
    if isinstance(data,list):
        return[mongo_to_json(item)for item in data]
    if isinstance(data,dict):
        return{key:mongo_to_json(value)for key,value in data.items()}
    if isinstance(data,ObjectId):
        return str(data)
    return data

@router.get("/state")
def get_state():
    return manager.public_data()

@router.get("/results/latest")
def get_latest_matka_result():
    collection=get_result_collection()
    doc=collection.find_one({"Result":True})
    if not doc:
        return{"success":False,"message":"No result found","Result":{}}
    return mongo_to_json(doc)

@router.get("/results/by-date/{date_key}")
def get_matka_result_by_date(date_key:str):
    collection=market_db[date_key]
    doc=collection.find_one({"Result":True})
    if not doc:
        return{"success":False,"message":"No result found","Result":{}}
    return mongo_to_json(doc)

@router.post("/bet")
async def place_bet(req:MatkaBetRequest):
    return await manager.place_bet(req)

@router.post("/clear")
async def clear_bets(req:MatkaClearRequest):
    return await manager.clear_bets(req)

async def matka_socket(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/market-message")
def handle_market_message(req:MarketMessageRequest):
    user_input=req.message.strip()
    time_key=req.time_key

    try:
        ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG=h(user_input,time_key)

        if not RESULT_LIST:
            return {
                "success":False,
                "reply":"GAME KA FORMAT SAHI NAHI HAI",
                "format":"ANK,ANK = AMOUNT | JODI = AMOUNT"
            }

        # mongo_client["casino"]["market_messages"].insert_one({
        #     "client_id":req.client_id,
        #     "user_id":req.user_id,
        #     "market_name":req.market_name,
        #     "time_key":time_key,
        #     "message":user_input,
        #     "action":ACTION,
        #     "result":RESULT_LIST,
        #     "total":TOTAL,
        #     "analysis":HLA_ANALYSIS,
        #     "flag":FLAG,
        #     "status":"pending_confirm",
        #     "created_at":datetime.datetime.utcnow()
        # })

        return {
            "success":True,
            "reply":"Confirm karna hai?",
            "market_name":req.market_name,
            "time_key":time_key,
            "result":RESULT_LIST,
            "total":TOTAL,
            "analysis":HLA_ANALYSIS
        }

    except Exception as e:
        return {
            "success":False,
            "reply":"HLA processing error",
            "error":str(e)
        }