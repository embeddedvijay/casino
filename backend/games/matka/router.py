import asyncio
import datetime
import os
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from core.tenant import bind_request_identity,user_security
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
from database import db as casino_db
from . import manager
from .schemas import MatkaBetRequest, MatkaClearRequest, MarketMessageRequest, MarketConfirmRequest
from pydantic import BaseModel
from hla_adv import adv_run as h
from .db_ops import add_data,get_play_collection_by_date,get_win_rates

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
                "value":value,
                "pana":pana,
                "open_value":_first_value(market_data,("OPEN","open")),
                "open_pana":_first_value(market_data,("OPANAL","OPANA","OPENPANA","openPana","open_pana")),
            })
    return events

def _matka_user_query(client_id,user_id):
    options=[{"user_id":str(user_id)},{"username":str(user_id)},{"mobile":str(user_id)}]
    if ObjectId.is_valid(str(user_id)):options.append({"_id":ObjectId(str(user_id))})
    return {"client_id":str(client_id),"$or":options}

def format_matka_market(market):
    market=str(market or "").strip()
    market_upper=market.upper()
    if market_upper.endswith("_OP"):
        return market[:-3].replace("_"," ").title(),"Open"
    if market_upper.endswith("_CL"):
        return market[:-3].replace("_"," ").title(),"Close"
    return market.replace("_"," ").title(),""

def _entry_amounts(result_rows,winning_keys):
    totals={key:0.0 for key in winning_keys}
    for row in result_rows or []:
        if not isinstance(row,(list,tuple)) or len(row)<2:continue
        try:amount=abs(float(row[-1]))
        except (TypeError,ValueError):continue
        selected={str(value).strip() for value in row[:-1]}
        for key in winning_keys:
            if key and key in selected:totals[key]+=amount
    return totals

def _requires_close_settlement(bet):
    """OP bets with Jodi/Sangam selections remain open until CLOSE result."""
    for row in bet.get("Result") or []:
        if not isinstance(row,(list,tuple)) or len(row)<2:continue
        for value in row[:-1]:
            token=str(value).strip()
            if "-" in token or (token.isdigit() and len(token)==2):return True
    return False

def _event_payout(bet,event,rates):
    session=event["session"]
    market=str(bet.get("Market") or "")
    result_rows=bet.get("Result") or []
    if session=="OPEN" and market==f'{event["market_name"]}_OP':
        keys={"ank":event["value"],"pana":event["pana"]}
        totals=_entry_amounts(result_rows,set(keys.values()))
        pana_rate=rates["TP"] if len(set(event["pana"]))==1 else rates["DP"] if len(set(event["pana"]))==2 else rates["SP"]
        return totals.get(keys["ank"],0)*rates["ANK"]+totals.get(keys["pana"],0)*pana_rate,"open"
    if session=="CLOSE" and market==f'{event["market_name"]}_CL':
        keys={"ank":event["value"],"pana":event["pana"]}
        totals=_entry_amounts(result_rows,set(keys.values()))
        pana_rate=rates["TP"] if len(set(event["pana"]))==1 else rates["DP"] if len(set(event["pana"]))==2 else rates["SP"]
        return totals.get(keys["ank"],0)*rates["ANK"]+totals.get(keys["pana"],0)*pana_rate,"close"
    if session=="CLOSE" and market==f'{event["market_name"]}_OP':
        op=event.get("open_value","");op_pana=event.get("open_pana","")
        keys={"jodi":f"{op}{event['value']}","full":f"{op_pana}-{event['pana']}","half_a":f"{op_pana}-{event['value']}","half_b":f"{op}-{event['pana']}"}
        totals=_entry_amounts(result_rows,set(keys.values()))
        payout=totals.get(keys["jodi"],0)*rates["Jodi"]+totals.get(keys["full"],0)*rates["FS"]+(totals.get(keys["half_a"],0)+totals.get(keys["half_b"],0))*rates["HS"]
        return payout,"combination"
    return 0.0,"skip"

def settle_matka_events(events,date_key):
    play_collection=get_play_collection_by_date(date_key)
    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    credited=0;settled=0
    for event in events:
        if event["session"]=="OPEN":markets=[f'{event["market_name"]}_OP']
        else:markets=[f'{event["market_name"]}_CL',f'{event["market_name"]}_OP']
        for bet in play_collection.find({"Market":{"$in":markets},"Action":{"$regex":"✅"}}):
            client_id=str(bet.get("client_id") or bet.get("Client") or "demo")
            rates=bet.get("WinRates") or get_win_rates(client_id)
            payout,part=_event_payout(bet,event,rates)
            if part=="skip":continue
            settlement_key=f'{event["event_key"]}:{bet["_id"]}:{part}'
            flag=f"settlement_parts.{part}"
            if bet.get("settlement_parts",{}).get(part):continue
            payout=round(max(0.0,float(payout)),2)
            user=raw_casino_db.users.find_one(_matka_user_query(client_id,bet.get("Contact")),{"_id":1,"balance":1})
            if not user:continue
            if payout>0:
                updated=raw_casino_db.users.find_one_and_update(
                    {"_id":user["_id"],"client_id":client_id,"credited_matka_win_ids":{"$ne":settlement_key}},
                    {"$inc":{"balance":payout},"$addToSet":{"credited_matka_win_ids":settlement_key},"$set":{"updated_at":datetime.datetime.utcnow()}},
                    return_document=ReturnDocument.AFTER,
                )
                raw_casino_db.wallet_transactions.update_one(
                    {"settlement_key":settlement_key},
                    {"$setOnInsert":{"settlement_key":settlement_key,"client_id":client_id,"user_id":str(user["_id"]),"user_ref":user["_id"],"type":"matka_win","amount":payout,"market":bet.get("Market"),"result":event["result"],"bet_id":str(bet["_id"]),"status":"completed","created_at":datetime.datetime.utcnow()}},
                    upsert=True,
                )
                if updated:credited+=1
                # Upsert even on a retry after a process interruption. The
                # user-level settlement token prevents a second wallet credit.
                market_name,market_side=format_matka_market(bet.get("Market"))
                market_label=f"{market_name} • {market_side}" if market_side else market_name
                raw_casino_db.notifications.update_one(
                    {"notification_key":f"matka-win:{settlement_key}"},
                    {"$setOnInsert":{"notification_key":f"matka-win:{settlement_key}","client_id":client_id,"user_id":str(user["_id"]),"type":"matka_win","title":"Matka Win","text":f'{market_label} • ₹{payout:,.2f} credited',"market_name":market_name,"market_side":market_side,"market":bet.get("Market"),"read":False,"created_at":datetime.datetime.utcnow()}},
                    upsert=True,
                )
            settlement_update={
                "$set":{
                    flag:True,
                    f"settlement_payouts.{part}":payout,
                    "updated_at":datetime.datetime.utcnow(),
                },
                "$inc":{"Win_Amt":payout},
            }
            final_settlement=(
                part in {"close","combination"}
                or (part=="open" and not _requires_close_settlement(bet))
            )
            if final_settlement:
                settlement_update["$set"].update({
                    "Settled":True,
                    "SettlementStatus":"settled",
                    "SettledAt":datetime.datetime.utcnow(),
                })
            else:
                settlement_update["$set"]["SettlementStatus"]="partially_settled"
            marked=play_collection.update_one(
                {"_id":bet["_id"],flag:{"$ne":True}},
                settlement_update,
            )
            if marked.modified_count:settled+=1
    return {"settled":settled,"credited":credited}

def sync_matka_result_notifications():
    """Settle Matka wins and remove legacy global result notifications."""
    collection=get_result_collection()
    doc=collection.find_one({"Result":True})
    if not doc:
        return 0

    events=extract_matka_result_events(doc,collection.name)
    if not events:
        return 0
    settlement=settle_matka_events(events,collection.name)
    if settlement["credited"]:
        print(f'✅ Matka wallet wins credited: {settlement["credited"]}')

    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    raw_casino_db.notifications.delete_many({"type":"matka_result"})
    return settlement["credited"]

def ensure_matka_notification_indexes():
    raw_casino_db=getattr(casino_db,"_raw",casino_db)
    raw_casino_db.notifications.create_index(
        "notification_key",unique=True,sparse=True,name="uniq_notification_key"
    )
    raw_casino_db.notifications.create_index(
        [("user_id",1),("created_at",-1)],name="user_notifications_latest"
    )
    raw_casino_db.wallet_transactions.create_index(
        "settlement_key",unique=True,sparse=True,name="uniq_matka_settlement_key"
    )

async def matka_result_notification_loop():
    poll_seconds=max(2,int(os.getenv("MATKA_RESULT_POLL_SECONDS","5")))
    while True:
        try:
            inserted=await asyncio.to_thread(sync_matka_result_notifications)
            if inserted:
                print(f"✅ Matka wallet wins credited: {inserted}")
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
async def place_bet(req:MatkaBetRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return await manager.place_bet(req)

@router.post("/clear")
async def clear_bets(req:MatkaClearRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return await manager.clear_bets(req)

async def matka_socket(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/market-message")
def handle_market_message(req:MarketMessageRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
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
def confirm_market_message(req:MarketConfirmRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
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
            {"_id":existing_user["_id"],"client_id":req.client_id,"balance":{"$gte":debit_amount}},
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
            "WinRates":get_win_rates(req.client_id),
            "dynamic_validation":True
        }

        saved=add_data(user_play_data)

        if not saved:
            raw_casino_db.users.update_one({"_id":debited_user_id,"client_id":req.client_id},{"$inc":{"balance":debit_amount}})
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

        market_name,market_side=format_matka_market(time_key)
        market_label=f"{market_name} • {market_side}" if market_side else market_name
        try:
            raw_casino_db.notifications.update_one(
                {"notification_key":f'matka-play:{user_play_data["Message_ID"]}'},
                {"$setOnInsert":{
                    "notification_key":f'matka-play:{user_play_data["Message_ID"]}',
                    "client_id":req.client_id,
                    "user_id":str(existing_user["_id"]),
                    "type":"matka_play",
                    "title":"Matka Play",
                    "text":f'{market_label} • ₹{debit_amount:,.2f} played',
                    "market_name":market_name,
                    "market_side":market_side,
                    "market":time_key,
                    "amount":debit_amount,
                    "read":False,
                    "created_at":datetime.datetime.utcnow(),
                }},
                upsert=True,
            )
        except Exception:
            pass

        return {"success":True,"message":"Market message confirmed successfully","total":TOTAL,"result":RESULT_LIST,"balance":round(float(updated_user.get("balance",0) or 0),2)}

    except Exception as e:
        if debited_user_id is not None and debit_amount>0:
            raw_casino_db.users.update_one({"_id":debited_user_id,"client_id":req.client_id},{"$inc":{"balance":debit_amount}})
        return {"success":False,"message":"Confirm failed","error":str(e)}
