import asyncio
import datetime
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
from database import db as casino_db
from . import manager
from .schemas import MatkaBetRequest, MatkaClearRequest, MarketMessageRequest, MarketConfirmRequest
from pydantic import BaseModel
from hla_adv import adv_run as h
from .db_ops import add_data

router=APIRouter(prefix="/api/games/matka",tags=["Matka"])

# Casino users/wallet continue using the main cloud MONGO_URI. Matka results
# are maintained by the existing local result service in the Market database,
# so this router uses a dedicated connection only for result reads.
MATKA_RESULT_MONGO_URI=os.getenv(
    "MATKA_RESULT_MONGO_URI",
    "mongodb://127.0.0.1:27017",
)
MATKA_RESULT_DB_NAME=os.getenv("MATKA_RESULT_DB_NAME","Market")
result_mongo_client=MongoClient(
    MATKA_RESULT_MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    appname="gold365-matka-results",
)
market_db=result_mongo_client[MATKA_RESULT_DB_NAME]

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

RESULT_METADATA_KEYS={"_id","Result","Date","CreatedAt","UpdatedAt","success","message"}
RESULT_SESSIONS=(
    ("OPEN",("OPEN","open"),("OPANAL","OPANA","OPENPANA","openPana","open_pana")),
    ("CLOSE",("CLOSE","close"),("CPANAL","CPANA","CLOSEPANA","closePana","close_pana")),
)

def _is_published_result(value):
    value="" if value is None else str(value).strip()
    return value not in {"","*","**","***","-","--",":--","None","null"}

def _first_value(data,keys):
    for key in keys:
        if key in data and _is_published_result(data.get(key)):
            return str(data[key]).strip()
    return ""

def extract_matka_result_events(doc,collection_name):
    """Return stable events for every published OPEN/CLOSE result."""
    result_source=doc.get("Result") if isinstance(doc.get("Result"),dict) else doc
    events=[]
    for market_name,market_data in result_source.items():
        if market_name in RESULT_METADATA_KEYS or not isinstance(market_data,dict):
            continue
        for session,value_keys,pana_keys in RESULT_SESSIONS:
            value=_first_value(market_data,value_keys)
            if not value:
                continue
            pana=_first_value(market_data,pana_keys)
            displayed_result=f"{pana}-{value}" if pana else value
            event_key=f"matka:{collection_name}:{market_name}:{session}:{displayed_result}"
            events.append({
                "event_key":event_key,
                "market_name":market_name,
                "market_label":market_name.replace("_"," ").title(),
                "session":session,
                "result":displayed_result,
            })
    return events

def sync_matka_result_notifications():
    """Insert each new result notification once for every active user."""
    collection=get_result_collection()
    doc=collection.find_one({"Result":True})
    if not doc:
        return 0

    events=extract_matka_result_events(doc,collection.name)
    if not events:
        return 0

    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    event_collection=raw_casino_db.matka_notification_events
    event_keys=[event["event_key"] for event in events]
    initialized=event_collection.find_one({"_id":"watcher_initialized"})
    if not initialized:
        # The first run is only a baseline. It must not broadcast all results
        # that were already published before this backend version started.
        for event_key in event_keys:
            event_collection.update_one(
                {"_id":event_key},
                {"$setOnInsert":{"created_at":datetime.datetime.utcnow()}},
                upsert=True,
            )
        event_collection.update_one(
            {"_id":"watcher_initialized"},
            {"$set":{"created_at":datetime.datetime.utcnow()}},
            upsert=True,
        )
        return 0

    users=list(raw_casino_db.users.find(
        {"status":{"$in":["active",None]}},
        {"_id":1,"client_id":1},
    ))
    inserted=0
    now=datetime.datetime.utcnow()
    for event in events:
        if event_collection.find_one({"_id":event["event_key"]},{"_id":1}):
            continue
        title=f'{event["market_label"]} {event["session"]} Result'
        text=f'{event["market_label"]} {event["session"]}: {event["result"]}'
        for user in users:
            notification_key=f'{event["event_key"]}:{user["_id"]}'
            result=raw_casino_db.notifications.update_one(
                {"notification_key":notification_key},
                {"$setOnInsert":{
                    "notification_key":notification_key,
                    "client_id":user.get("client_id"),
                    "user_id":str(user["_id"]),
                    "type":"matka_result",
                    "title":title,
                    "text":text,
                    "market_name":event["market_name"],
                    "session":event["session"],
                    "result":event["result"],
                    "read":False,
                    "created_at":now,
                }},
                upsert=True,
            )
            if result.upserted_id is not None:
                inserted+=1
        event_collection.update_one(
            {"_id":event["event_key"]},
            {"$setOnInsert":{"created_at":now}},
            upsert=True,
        )
    return inserted

def ensure_matka_notification_indexes():
    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    raw_casino_db.notifications.create_index(
        "notification_key",unique=True,sparse=True,name="uniq_notification_key"
    )
    raw_casino_db.notifications.create_index(
        [("user_id",1),("created_at",-1)],name="user_notifications_latest"
    )

async def matka_result_notification_loop():
    poll_seconds=max(2,int(os.getenv("MATKA_RESULT_POLL_SECONDS","5")))
    while True:
        try:
            inserted=await asyncio.to_thread(sync_matka_result_notifications)
            if inserted:
                print(f"✅ Matka result notifications sent: {inserted}")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"⚠️ Matka result notification error: {exc}")
        await asyncio.sleep(poll_seconds)

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
            return {"success":False,"reply":"GAME KA FORMAT SAHI NAHI HAI"}

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
        return {"success":False,"reply":"HLA processing error","error":str(e)}

@router.post("/market-message/confirm")
def confirm_market_message(req:MarketConfirmRequest):
    user_input=req.message.strip()
    market_name=req.market_name or req.market
    time_key=req.time_key or market_name

    debited_user_id=None
    debit_amount=0.0
    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    try:
        ACTION,RESULT_LIST,TOTAL,HLA_ANALYSIS,FLAG=h(user_input,time_key)

        if not RESULT_LIST:
            return {"success":False,"message":"Invalid bet data"}

        debit_amount=round(float(TOTAL or 0),2)
        if debit_amount<=0:
            return {"success":False,"message":"Invalid bet amount"}

        user_options=[
            {"user_id":req.user_id},
            {"username":req.user_id},
            {"mobile":req.user_id},
        ]
        if ObjectId.is_valid(req.user_id):
            user_options.append({"_id":ObjectId(req.user_id)})
        user_query={"client_id":req.client_id,"$or":user_options}
        existing_user=raw_casino_db.users.find_one(user_query,{"_id":1,"balance":1,"status":1})
        if not existing_user:
            return {"success":False,"message":"User account not found. Login again."}
        if existing_user.get("status","active")!="active":
            return {"success":False,"message":"User account is not active"}

        updated_user=raw_casino_db.users.find_one_and_update(
            {"_id":existing_user["_id"],"balance":{"$gte":debit_amount}},
            {"$inc":{"balance":-debit_amount},"$set":{"updated_at":datetime.datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated_user:
            available=round(float(existing_user.get("balance",0) or 0),2)
            return {"success":False,"message":f"Insufficient balance. Available ₹{available:.2f}, required ₹{debit_amount:.2f}"}
        debited_user_id=existing_user["_id"]

        user_play_data={
            "Client":req.client_id,
            "Contact":req.user_id,
            "Time":datetime.datetime.now().strftime("%H:%M:%S"),
            "Message":user_input,
            "Message_ID":str(int(datetime.datetime.utcnow().timestamp()*1000)),
            "Market":time_key,
            "Action":"✅",
            "Result":RESULT_LIST,
            "Total":TOTAL,
            "Settled":False,
            "Analysis":HLA_ANALYSIS,
            "dynamic_validation":True
        }

        saved=add_data(user_play_data)

        if not saved:
            raw_casino_db.users.update_one({"_id":debited_user_id},{"$inc":{"balance":debit_amount}})
            debited_user_id=None
            return {"success":False,"message":"DB save failed"}

        # The play is now durable, so never refund it because of an auxiliary
        # ledger write failure (that would create a free bet).
        debited_user_id=None
        try:
            raw_casino_db.wallet_transactions.insert_one({
                "client_id":req.client_id,
                "user_id":str(existing_user["_id"]),
                "user_ref":existing_user["_id"],
                "type":"matka_bet",
                "amount":-debit_amount,
                "market":time_key,
                "message":user_input,
                "status":"completed",
                "balance":round(float(updated_user.get("balance",0) or 0),2),
                "created_at":datetime.datetime.utcnow(),
            })
        except Exception:
            pass

        return {"success":True,"message":"Market message confirmed successfully","total":TOTAL,"result":RESULT_LIST,"balance":round(float(updated_user.get("balance",0) or 0),2)}

    except Exception as e:
        if debited_user_id is not None and debit_amount>0:
            raw_casino_db.users.update_one({"_id":debited_user_id},{"$inc":{"balance":debit_amount}})
        return {"success":False,"message":"Confirm failed","error":str(e)}
