from datetime import datetime, timedelta, timezone
import os

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from pymongo import ReturnDocument, MongoClient

from admin.dependencies import current_admin
from database import db
from games.matka.db_ops import get_play_collection


router = APIRouter(prefix="/api/admin", tags=["Admin Mobile Operations"])


def now():
    return datetime.now(timezone.utc)


def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    return value


def user_id_query(user_id: str, client_id: str):
    options = [{"user_id": user_id}, {"username": user_id}, {"mobile": user_id}]
    if ObjectId.is_valid(user_id):
        options.append({"_id": ObjectId(user_id)})
    return {"client_id": client_id, "$or": options}


class BalanceAdjustment(BaseModel):
    operation: str = Field(pattern="^(deposit|withdrawal)$")
    amount: float = Field(gt=0, le=100000000)
    reason: str = Field(min_length=3, max_length=200)
    reference: str = Field(default="", max_length=100)
    remarks: str = Field(default="", max_length=500)


class UpiSettings(BaseModel):
    upi_id: str = Field(min_length=3, max_length=100)
    payee_name: str = Field(min_length=2, max_length=100)
    enabled: bool = True
    instructions: str = Field(default="", max_length=500)


class OfferSend(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    message: str = Field(min_length=3, max_length=500)
    target: str = Field(default="all", pattern="^(all|active|selected)$")
    user_ids: list[str] = Field(default_factory=list, max_length=500)
    expires_at: datetime | None = None


@router.get("/users")
def admin_users(
    search: str = "",
    status_filter: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    admin: dict = Depends(current_admin),
):
    query = {"client_id": admin["client_id"]}
    if status_filter:
        query["status"] = status_filter
    if search.strip():
        escaped = search.strip()
        query["$or"] = [
            {"full_name": {"$regex": escaped, "$options": "i"}},
            {"mobile": {"$regex": escaped, "$options": "i"}},
            {"username": {"$regex": escaped, "$options": "i"}},
        ]
    users = list(db.users.find(query, {"password": 0, "password_hash": 0, "password_salt": 0}).sort("created_at", -1).limit(limit))
    return {"users": serialize(users)}


@router.post("/users/{user_id}/balance-adjustment")
def adjust_balance(user_id: str, body: BalanceAdjustment, admin: dict = Depends(current_admin)):
    query = user_id_query(user_id, admin["client_id"])
    amount = round(float(body.amount), 2)
    before = db.users.find_one(query)
    if not before:
        raise HTTPException(status_code=404, detail="User not found")
    update_query = dict(query)
    delta = amount if body.operation == "deposit" else -amount
    if body.operation == "withdrawal":
        update_query["balance"] = {"$gte": amount}
    user = db.users.find_one_and_update(
        update_query,
        {"$inc": {"balance": delta}, "$set": {"updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    transaction = {
        "client_id": admin["client_id"], "user_id": str(user.get("_id")), "user_ref": user["_id"],
        "type": "admin_deposit" if body.operation == "deposit" else "admin_withdrawal",
        "amount": delta, "reason": body.reason, "reference": body.reference,
        "remarks": body.remarks, "admin": admin["username"], "created_at": now(),
    }
    saved = db.wallet_transactions.insert_one(transaction)
    db.audit_logs.insert_one({
        "client_id": admin["client_id"], "admin": admin["username"], "action": "balance_adjustment",
        "user_id": str(user["_id"]), "operation": body.operation, "amount": amount,
        "before_balance": float(before.get("balance", 0)), "after_balance": float(user.get("balance", 0)),
        "reason": body.reason, "reference_id": str(saved.inserted_id), "created_at": now(),
    })
    clean = serialize(user); clean.pop("password", None); clean.pop("password_hash", None); clean.pop("password_salt", None)
    return {"success": True, "user": clean, "transaction_id": str(saved.inserted_id)}


@router.get("/analytics")
def analytics(period: str = Query("day", pattern="^(day|week)$"), admin: dict = Depends(current_admin)):
    days = 1 if period == "day" else 7
    start = now() - timedelta(days=days)
    match = {"client_id": admin["client_id"], "created_at": {"$gte": start}}
    timeline = list(db.casino_bets.aggregate([
        {"$match": match},
        {"$group": {"_id": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "game": "$game"},
                     "play": {"$sum": "$amount"}, "win": {"$sum": "$payout"}, "bets": {"$sum": 1}}},
        {"$sort": {"_id.day": 1, "play": -1}},
    ]))
    games = list(db.casino_bets.aggregate([
        {"$match": match},
        {"$group": {"_id": "$game", "play": {"$sum": "$amount"}, "win": {"$sum": "$payout"}, "bets": {"$sum": 1},
                     "players": {"$addToSet": "$user_id"}}},
        {"$project": {"game": "$_id", "_id": 0, "play": 1, "win": 1, "bets": 1, "players": {"$size": "$players"},
                      "net": {"$subtract": ["$play", "$win"]}}},
        {"$sort": {"play": -1}},
    ]))
    total_play = sum(float(row.get("play", 0)) for row in games)
    total_win = sum(float(row.get("win", 0)) for row in games)
    most_played = max(games, key=lambda row: row.get("play", 0), default=None)
    most_won = max(games, key=lambda row: row.get("win", 0), default=None)
    return serialize({"period": period, "from": start, "total_play": total_play, "total_win": total_win,
                      "casino_net": total_play-total_win, "games": games, "timeline": timeline,
                      "most_played": most_played, "most_won": most_won})


@router.get("/payment-settings/upi")
def get_upi(admin: dict = Depends(current_admin)):
    row = db.payment_settings.find_one({"client_id": admin["client_id"], "type": "upi"}, {"_id": 0})
    return row or {"client_id": admin["client_id"], "type": "upi", "upi_id": "", "payee_name": "", "enabled": False, "instructions": ""}


@router.put("/payment-settings/upi")
def save_upi(body: UpiSettings, admin: dict = Depends(current_admin)):
    values = {**body.model_dump(), "client_id": admin["client_id"], "type": "upi", "updated_at": now(), "updated_by": admin["username"]}
    db.payment_settings.update_one({"client_id": admin["client_id"], "type": "upi"}, {"$set": values}, upsert=True)
    db.audit_logs.insert_one({"client_id": admin["client_id"], "admin": admin["username"], "action": "upi_settings_updated", "created_at": now()})
    return {"success": True, "settings": serialize(values)}


@router.post("/offers/send")
def send_offer(body: OfferSend, admin: dict = Depends(current_admin)):
    query = {"client_id": admin["client_id"]}
    if body.target == "active":
        query["status"] = "active"
    elif body.target == "selected":
        query["$or"] = [{"user_id": {"$in": body.user_ids}}, {"username": {"$in": body.user_ids}}]
    users = list(db.users.find(query, {"_id": 1, "user_id": 1, "username": 1}))
    offer = {**body.model_dump(), "client_id": admin["client_id"], "sent_by": admin["username"], "recipient_count": len(users), "created_at": now()}
    offer_id = db.offers.insert_one(offer).inserted_id
    if users:
        db.user_notifications.insert_many([{
            "client_id": admin["client_id"], "user_ref": user["_id"], "user_id": str(user.get("user_id") or user.get("username") or user["_id"]),
            "type": "offer", "offer_id": offer_id, "title": body.title, "message": body.message,
            "read": False, "created_at": now(), "expires_at": body.expires_at,
        } for user in users])
    db.audit_logs.insert_one({"client_id": admin["client_id"], "admin": admin["username"], "action": "offer_sent", "offer_id": str(offer_id), "recipients": len(users), "created_at": now()})
    return {"success": True, "offer_id": str(offer_id), "recipient_count": len(users)}


@router.get("/audit-logs")
def audit_logs(limit: int = Query(100, ge=1, le=500), admin: dict = Depends(current_admin)):
    rows = list(db.audit_logs.find({"client_id": admin["client_id"]}).sort("created_at", -1).limit(limit))
    return {"logs": serialize(rows)}


@router.get("/database/health")
def database_health(admin: dict = Depends(current_admin)):
    primary = "connected"
    try:
        getattr(db, "_raw", db).command("ping")
    except Exception:
        primary = "down"
    secondary_uri = os.getenv("SECONDARY_MONGO_URI", "").strip()
    secondary = "not_configured"
    if secondary_uri:
        try:
            MongoClient(secondary_uri, serverSelectionTimeoutMS=2500).admin.command("ping")
            secondary = "connected"
        except Exception:
            secondary = "down"
    return {"primary": {"status": primary}, "secondary": {"status": secondary}}


@router.get("/matka/messages")
def matka_messages(
    market_key: str = Query(..., min_length=2, max_length=80),
    session: str = Query(..., pattern="^(open|close)$"),
    limit: int = Query(200, ge=1, le=500),
    admin: dict = Depends(current_admin),
):
    suffix = "OP" if session == "open" else "CL"
    normalized_key = market_key.strip().upper().replace(" ", "_")
    # The UI may send either KALYAN or an already expanded KALYAN_OP/KALYAN_CL.
    # Stored play documents always use one final session suffix in `Market`.
    for existing_suffix in ("_OP", "_CL"):
        if normalized_key.endswith(existing_suffix):
            normalized_key = normalized_key[:-len(existing_suffix)]
            break
    time_key = f"{normalized_key}_{suffix}"
    collection = get_play_collection(admin["client_id"])
    # Read genuine bet messages only. Total=0 records are generated result/
    # forwarding summaries and can contain an OP list even under a CL key.
    query = {
        "Market": time_key,
        "Client": admin["client_id"],
        "Total": {"$gt": 0},
    }
    rows = list(collection.find(query).sort([("Time", -1), ("_id", -1)]).limit(limit))
    return {
        "market_key": normalized_key,
        "session": session,
        "time_key": time_key,
        "count": len(rows),
        "messages": [serialize({
            "id": row.get("_id"),
            "client": row.get("Client", ""),
            "contact": row.get("Contact", ""),
            "market": row.get("Market", ""),
            "message": row.get("Message", ""),
            "message_id": row.get("Message_ID", ""),
            "time": row.get("Time", ""),
            "total": row.get("Total", 0),
            "action": row.get("Action", ""),
            "result": row.get("Result", []),
            "analysis": row.get("Analysis"),
            "dynamic_validation": bool(row.get("dynamic_validation", False)),
            "settled": bool(row.get("Settled", False)),
        }) for row in rows],
    }
