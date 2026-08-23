from datetime import datetime, timezone
from secrets import SystemRandom

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

from database import db


RNG = SystemRandom()
LEVELS = {
    "easy": {"safe_probability": 0.91, "multipliers": [1.10, 1.25, 1.50, 1.85, 2.30, 3.00, 4.10, 5.70, 8.00, 12.00]},
    "medium": {"safe_probability": 0.84, "multipliers": [1.15, 1.40, 1.80, 2.40, 3.30, 4.70, 7.00, 10.50, 16.00, 25.00]},
    "hard": {"safe_probability": 0.72, "multipliers": [1.25, 1.70, 2.50, 3.80, 6.00, 10.00, 17.00, 30.00, 55.00, 100.00]},
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
    return {
        "success": True,
        "min_bet": 10,
        "max_bet": 10000,
        "levels": {key: value["multipliers"] for key, value in LEVELS.items()},
    }


def start(user_id, amount, difficulty):
    difficulty = str(difficulty).lower()
    if difficulty not in LEVELS:
        raise HTTPException(400, "Difficulty must be easy, medium or hard")
    amount = round(float(amount), 2)
    if amount < 10 or amount > 10000:
        raise HTTPException(400, "Bet must be between 10 and 10000")
    ensure_demo(user_id)
    query = user_filter(user_id)
    user = db.users.find_one_and_update(
        {"$and": [query, {"balance": {"$gte": amount}}, {"status": {"$nin": ["blocked", "inactive"]}}]},
        {"$inc": {"balance": -amount}, "$set": {"updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not user:
        if not db.users.find_one(query):
            raise HTTPException(404, "User not found")
        raise HTTPException(400, "Insufficient balance or account blocked")
    document = {
        "user_id": str(user_id), "user_ref": user["_id"], "game": "chicken-road",
        "amount": amount, "bet": amount, "difficulty": difficulty, "step": 0,
        "multiplier": 1.0, "payout": 0.0, "profit": -amount, "status": "active",
        "created_at": now(), "updated_at": now(),
    }
    result = db.chicken_road_bets.insert_one(document)
    return {
        "success": True, "round_id": str(result.inserted_id), "status": "active",
        "step": 0, "multiplier": 1.0, "balance": round(float(user.get("balance", 0)), 2),
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
    user = db.users.find_one_and_update(
        {"_id": item["user_ref"]}, {"$inc": {"balance": payout}, "$set": {"updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "status": "won", "step": item["step"], "multiplier": item["multiplier"], "payout": payout, "profit": round(payout - item["amount"], 2), "balance": round(float(user.get("balance", 0)), 2)}


def history(user_id, limit=20):
    records = []
    for item in db.chicken_road_bets.find({"user_id": str(user_id), "status": {"$ne": "active"}}).sort("created_at", -1).limit(max(1, min(int(limit), 100))):
        item["id"] = str(item.pop("_id")); item.pop("user_ref", None)
        for key in ("created_at", "updated_at", "settled_at"):
            if item.get(key): item[key] = item[key].isoformat()
        records.append(item)
    return {"success": True, "history": records}
