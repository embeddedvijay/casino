

# GOLD365_DEMO_NO_BALANCE_V2
def _gold365_is_demo(user_id):
    return str(user_id or "").strip().lower() in {"demo", "demo123"}

from datetime import datetime, timezone
from secrets import SystemRandom
import uuid

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

from database import db
from core.casino import CasinoError, cancel_user_bets, game_settings, place_bet, settle_bet


RNG = SystemRandom()
LEVELS = {
    "easy": {"safe_probability": 0.94, "multipliers": [1.06, 1.14, 1.23, 1.34, 1.47, 1.62, 1.80, 2.03, 2.31, 2.68, 3.15, 3.78]},
    "medium": {"safe_probability": 0.87, "multipliers": [1.12, 1.28, 1.47, 1.70, 1.98, 2.33, 2.76, 3.32, 4.03, 4.96, 6.20, 6.91]},
    "hard": {"safe_probability": 0.78, "multipliers": [1.22, 1.52, 1.91, 2.43, 3.13, 4.10, 5.48, 7.50, 10.55, 15.35, 23.25, 37.20]},
    "hardcore": {"safe_probability": 0.65, "multipliers": [1.46, 2.12, 3.16, 4.86, 7.75, 12.90, 22.60, 42.30, 85.00, 185.00, 440.00, 1177.00]},
}


def now():
    return datetime.now(timezone.utc)


def user_filter(value):
    value = str(value or "").strip()
    if not value:
        raise HTTPException(400, "User ID required")
    options = [{"user_id": value}, {"username": value}, {"user_name": value}]
    if ObjectId.is_valid(value):
        options.append({"_id": ObjectId(value)})
    return {"$or": options}


def ensure_demo(value):
    if str(value).lower() != "demo":
        return
    db.users.update_one(
        {"user_id": "demo"},
        {
            "$set": {"username": "demo", "is_demo": True, "status": "active", "updated_at": now()},
            "$setOnInsert": {"balance": 1000.0, "currency": "INR", "created_at": now()},
        },
        upsert=True,
    )


def config():
    settings=game_settings("chicken-road")
    return {
        "success": True,
        "min_bet": settings["min_bet"],
        "max_bet": settings["max_bet"],
        "enabled": settings["enabled"],
        "levels": {key: value["multipliers"] for key, value in LEVELS.items()},
    }


def start(user_id, amount, difficulty):
    difficulty = str(difficulty).lower()
    if difficulty not in LEVELS:
        raise HTTPException(400, "Difficulty must be easy, medium, hard or hardcore")
    amount = round(float(amount), 2)
    ensure_demo(user_id)
    for old in db.chicken_road_bets.find({"user_id":str(user_id),"status":"active"}):
        cancel_user_bets("chicken-road",old.get("casino_round_id",str(old["_id"])),str(user_id))
    db.chicken_road_bets.update_many({"user_id":str(user_id),"status":"active"},{"$set":{"status":"cancelled","settled_at":now(),"updated_at":now()}})
    casino_round_id="CR-"+uuid.uuid4().hex
    try:
        saved=place_bet(game="chicken-road",round_id=casino_round_id,user_id=user_id,amount=amount,position_key="road",metadata={"difficulty":difficulty})
    except CasinoError as exc:
        raise HTTPException(400,str(exc)) from exc
    document = {
        "_id": ObjectId(saved["id"]), "casino_round_id":casino_round_id,
        "user_id": str(user_id), "game": "chicken-road",
        "amount": amount, "bet": amount, "difficulty": difficulty, "step": 0,
        "multiplier": 1.0, "payout": 0.0, "profit": -amount, "status": "active",
        "created_at": now(), "updated_at": now(),
    }
    try:
        result = db.chicken_road_bets.insert_one(document)
    except Exception:
        cancel_user_bets("chicken-road",casino_round_id,str(user_id))
        raise
    return {
        "success": True, "round_id": str(result.inserted_id), "status": "active",
        "step": 0, "multiplier": 1.0, "balance": saved["balance"],
        "multipliers": LEVELS[difficulty]["multipliers"],
    }


def active_round(round_id):
    if not ObjectId.is_valid(round_id):
        raise HTTPException(400, "Invalid round ID")
    item = db.chicken_road_bets.find_one({"_id": ObjectId(round_id), "status": "active"})
    if not item:
        raise HTTPException(404, "Active round not found")
    return item


def advance(round_id):
    item = active_round(round_id)
    level = LEVELS[item["difficulty"]]
    next_step = int(item["step"]) + 1
    if next_step > len(level["multipliers"]):
        raise HTTPException(400, "Finish reached; cash out")
    safe = RNG.random() < level["safe_probability"]
    multiplier = level["multipliers"][next_step - 1]
    if safe:
        updated = db.chicken_road_bets.find_one_and_update(
            {"_id": item["_id"], "status": "active", "step": item["step"]},
            {"$set": {"step": next_step, "multiplier": multiplier, "updated_at": now()}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raise HTTPException(409, "Round already updated")
        return {"success": True, "safe": True, "status": "active", "step": next_step, "multiplier": multiplier, "potential_win": round(item["amount"] * multiplier, 2)}
    updated = db.chicken_road_bets.find_one_and_update(
        {"_id": item["_id"], "status": "active", "step": item["step"]},
        {"$set": {"status": "lost", "step": next_step, "multiplier": 0.0, "payout": 0.0, "profit": -item["amount"], "settled_at": now(), "updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(409, "Round already updated")
    settle_bet(str(item["_id"]),0.0,{"step":next_step,"collision":True})
    return {"success": True, "safe": False, "status": "lost", "step": next_step, "multiplier": 0.0, "payout": 0.0}


def cash_out(round_id):
    item = active_round(round_id)
    if int(item["step"]) < 1:
        raise HTTPException(400, "Take at least one step before cash out")
    payout = round(float(item["amount"]) * float(item["multiplier"]), 2)
    settled = db.chicken_road_bets.find_one_and_update(
        {"_id": item["_id"], "status": "active", "step": item["step"]},
        {"$set": {"status": "won", "payout": payout, "profit": round(payout - item["amount"], 2), "settled_at": now(), "updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not settled:
        raise HTTPException(409, "Round already settled")
    casino_bet=settle_bet(str(item["_id"]),payout,{"step":item["step"],"multiplier":item["multiplier"]})
    if not casino_bet:
        raise HTTPException(409,"Round already settled")
    return {"success": True, "status": "won", "step": item["step"], "multiplier": item["multiplier"], "payout": payout, "profit": round(payout - item["amount"], 2), "balance": casino_bet["balance"]}


def history(user_id, limit=20):
    records = []
    for item in db.chicken_road_bets.find({"user_id": str(user_id), "status": {"$ne": "active"}}).sort("created_at", -1).limit(max(1, min(int(limit), 100))):
        item["id"] = str(item.pop("_id")); item.pop("user_ref", None)
        for key in ("created_at", "updated_at", "settled_at"):
            if item.get(key): item[key] = item[key].isoformat()
        records.append(item)
    return {"success": True, "history": records}
