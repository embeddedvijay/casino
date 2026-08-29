from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from io import BytesIO
import re
from typing import Any
from urllib.parse import urlencode

from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument
import qrcode


BET_COLLECTIONS = (
    ("aviator_bets", "aviator"),
    ("dragon_tiger_bets", "dragon-tiger"),
    ("lucky_race_bets", "lucky-race"),
    ("car_roulet_bets", "lucky-race"),
    ("matka_bets", "matka"),
    ("teen_patti_bets", "teen-patti"),
    ("andar_bahar_bets", "andar-bahar"),
    ("plinko_bets", "plinko"),
    ("chicken_road_bets", "chicken-road"),
    ("bets", None),
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def serialize(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def user_query(user_id: str) -> dict:
    choices: list[dict] = [
        {"user_id": user_id},
        {"username": user_id},
        {"user_name": user_id},
        {"mobile": user_id},
    ]
    if ObjectId.is_valid(user_id):
        choices.append({"_id": ObjectId(user_id)})
    return {"$or": choices}


def get_user(db, user_id: str) -> dict | None:
    user = db.users.find_one(user_query(user_id), {"password": 0, "password_hash": 0, "salt": 0, "otp": 0})
    return serialize(user) if user else None


def update_user(db, user_id: str, changes: dict) -> dict | None:
    allowed = {"name", "email", "mobile", "avatar", "language"}
    payload = {key: value for key, value in changes.items() if key in allowed and value is not None}
    if payload:
        payload["updated_at"] = utcnow()
        db.users.update_one(user_query(user_id), {"$set": payload})
    return get_user(db, user_id)


def balance_for(user: dict) -> float:
    return float(user.get("balance", user.get("wallet_balance", 0)) or 0)


def transaction_query(user_id: str) -> dict:
    return {"$or": [{"user_id": user_id}, {"username": user_id}, {"user_name": user_id}]}


def list_transactions(db, user_id: str, page: int, limit: int, kind: str | None = None) -> dict:
    query = transaction_query(user_id)
    if kind and kind != "all":
        query = {"$and": [query, {"type": kind}]}
    collection = db.wallet_transactions
    total = collection.count_documents(query)
    cursor = collection.find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).skip((page - 1) * limit).limit(limit)
    return {"items": serialize(list(cursor)), "page": page, "limit": limit, "total": total, "has_more": page * limit < total}


def wallet_summary(db, user_id: str) -> dict | None:
    user = get_user(db, user_id)
    if not user:
        return None
    query = transaction_query(user_id)
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$type", "amount": {"$sum": {"$ifNull": ["$amount", 0]}}}},
    ]
    totals = {str(item["_id"]): float(item["amount"] or 0) for item in db.wallet_transactions.aggregate(pipeline)}
    approved_deposit = list(db.wallet_transactions.aggregate([
        {"$match": {"$and": [query, {"type": "deposit"}, {"status": {"$in": ["approved", "completed", "success"]}}]}},
        {"$group": {"_id": None, "amount": {"$sum": {"$ifNull": ["$amount", 0]}}}},
    ]))
    totals["deposit"] = float(approved_deposit[0]["amount"] or 0) if approved_deposit else 0
    return {
        "user_id": user.get("user_id", user_id),
        "balance": balance_for(user),
        "currency": user.get("currency", "INR"),
        "total_deposit": totals.get("deposit", 0),
        "total_withdrawal": totals.get("withdrawal", 0),
        "total_winnings": totals.get("win", totals.get("winning", 0)),
    }


def bet_owner_query(user_id: str) -> dict:
    return {"$or": [{"user_id": user_id}, {"username": user_id}, {"user_name": user_id}, {"player_id": user_id}]}


def list_bets(db, user_id: str, page: int, limit: int, game: str | None = None, status: str | None = None) -> dict:
    rows: list[dict] = []
    for collection_name, default_game in BET_COLLECTIONS:
        if collection_name not in db.list_collection_names():
            continue
        if game and game != "all" and default_game and default_game != game:
            continue
        query: dict = bet_owner_query(user_id)
        if status and status != "all":
            query = {"$and": [query, {"status": {"$regex": f"^{status}$", "$options": "i"}}]}
        for row in db[collection_name].find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(500):
            item = serialize(row)
            item.setdefault("game", default_game or item.get("game", "unknown"))
            item["collection"] = collection_name
            rows.append(item)
    rows.sort(key=lambda item: str(item.get("created_at", item.get("placed_at", ""))), reverse=True)
    total = len(rows)
    start = (page - 1) * limit
    return {"items": rows[start:start + limit], "page": page, "limit": limit, "total": total, "has_more": start + limit < total}


def list_promotions(db) -> list[dict]:
    now = utcnow()
    query = {
        "status": {"$in": ["active", "Active", True]},
        "$and": [
            {"$or": [{"starts_at": {"$exists": False}}, {"starts_at": None}, {"starts_at": {"$lte": now}}]},
            {"$or": [{"ends_at": {"$exists": False}}, {"ends_at": None}, {"ends_at": {"$gte": now}}]},
        ],
    }
    return serialize(list(db.promotions.find(query).sort([("priority", DESCENDING), ("created_at", DESCENDING)])))


def create_ticket(db, user_id: str, subject: str, message: str, category: str) -> dict:
    document = {
        "ticket_id": f"TKT-{int(utcnow().timestamp() * 1000)}",
        "user_id": user_id,
        "subject": subject.strip(),
        "message": message.strip(),
        "category": category,
        "status": "open",
        "replies": [],
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    result = db.support_tickets.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize(document)


def list_tickets(db, user_id: str, page: int, limit: int) -> dict:
    query = {"user_id": user_id}
    total = db.support_tickets.count_documents(query)
    rows = list(db.support_tickets.find(query).sort([("updated_at", DESCENDING), ("_id", DESCENDING)]).skip((page - 1) * limit).limit(limit))
    return {"items": serialize(rows), "page": page, "limit": limit, "total": total, "has_more": page * limit < total}


def create_wallet_request(
    db,
    user_id: str,
    request_type: str,
    amount: float,
    method: str,
    reference: str | None = None,
) -> dict:
    user = get_user(db, user_id)
    if not user:
        raise ValueError("User not found")
    if request_type == "withdrawal" and amount > balance_for(user):
        raise ValueError("Insufficient wallet balance")
    now = utcnow()
    prefix = "DPS" if request_type == "deposit" else "WDR"
    transaction = {
        "transaction_id": f"{prefix}{int(now.timestamp() * 1000)}",
        "user_id": user_id,
        "type": request_type,
        "amount": float(amount),
        "method": method,
        "reference": reference or "",
        "status": "pending",
        "currency": user.get("currency", "INR"),
        "created_at": now,
        "updated_at": now,
    }
    result = db.wallet_transactions.insert_one(transaction)
    transaction["_id"] = result.inserted_id
    db.notifications.insert_one({
        "user_id": user_id,
        "title": f"{request_type.title()} submitted",
        "text": f"Your {request_type} request of ₹{amount:,.2f} is under review.",
        "type": request_type,
        "read": False,
        "created_at": now,
    })
    return serialize(transaction)


def create_deposit_qr(db, user_id: str, amount: float) -> dict:
    amount = round(float(amount), 2)
    if amount < 500:
        raise ValueError("Minimum deposit amount is ₹500")
    user = db.users.find_one(user_query(user_id), {"password": 0, "password_hash": 0, "salt": 0, "otp": 0})
    if not user:
        raise ValueError("User not found")
    client_id = str(user.get("client_id") or "demo")
    settings = db.payment_settings.find_one({"client_id": client_id, "type": "upi", "enabled": True})
    if not settings or not str(settings.get("upi_id") or "").strip():
        raise ValueError("UPI payment is temporarily unavailable")

    now = utcnow()
    mobile = str(user.get("mobile") or user.get("username") or user.get("user_id") or "")
    digits = re.sub(r"\D", "", mobile)
    last_four = (digits[-4:] if len(digits) >= 4 else str(user["_id"])[-4:]).upper()
    reference = f"{last_four}{now.strftime('%H%M%S')}{now.microsecond // 1000:03d}"
    payee_name = str(settings.get("payee_name") or "GOLD365").strip()
    upi_id = str(settings["upi_id"]).strip()
    upi_uri = "upi://pay?" + urlencode({
        "pa": upi_id,
        "pn": payee_name,
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tr": reference,
        "tn": f"GOLD365 deposit {reference}",
    })
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=3)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#020519", back_color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    expires_at = now + timedelta(minutes=30)
    canonical_user_id = str(user["_id"])
    session = {
        "reference": reference,
        "client_id": client_id,
        "user_id": canonical_user_id,
        "requested_user_id": str(user_id),
        "user_ref": user["_id"],
        "username": user.get("username") or user.get("user_name") or "",
        "mobile": user.get("mobile") or "",
        "full_name": user.get("full_name") or user.get("name") or "",
        "amount": amount,
        "currency": "INR",
        "upi_id": upi_id,
        "payee_name": payee_name,
        "upi_uri": upi_uri,
        "status": "created",
        "created_at": now,
        "expires_at": expires_at,
        "updated_at": now,
    }
    db.deposit_payment_sessions.insert_one(session)
    return serialize({
        "reference": reference,
        "amount": amount,
        "upi_id": upi_id,
        "payee_name": payee_name,
        "upi_uri": upi_uri,
        "qr_image": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii"),
        "instructions": settings.get("instructions") or "Pay the exact amount, then tap DONE.",
        "expires_at": expires_at,
    })


def submit_deposit_qr(db, user_id: str, reference: str) -> dict:
    user = db.users.find_one(user_query(user_id), {"_id": 1})
    if not user:
        raise ValueError("User not found")
    canonical_user_id = str(user["_id"])
    clean_reference = str(reference or "").strip().upper()
    existing = db.wallet_transactions.find_one({
        "type": "deposit",
        "qr_reference": clean_reference,
        "user_id": canonical_user_id,
    })
    if existing:
        return serialize(existing)

    now = utcnow()
    session = db.deposit_payment_sessions.find_one_and_update(
        {
            "reference": clean_reference,
            "user_id": canonical_user_id,
            "status": "created",
            "expires_at": {"$gt": now},
        },
        {"$set": {"status": "submitting", "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )
    if not session:
        row = db.deposit_payment_sessions.find_one({"reference": clean_reference, "user_id": canonical_user_id})
        if row and row.get("status") == "submitted":
            existing = db.wallet_transactions.find_one({"qr_reference": clean_reference, "user_id": canonical_user_id})
            if existing:
                return serialize(existing)
        if row and row.get("expires_at") and row["expires_at"] <= now:
            raise ValueError("Payment QR expired. Generate a new QR.")
        raise ValueError("Invalid or already submitted payment request")

    transaction = {
        "transaction_id": f"DPS{int(now.timestamp() * 1000)}",
        "client_id": session["client_id"],
        "user_id": canonical_user_id,
        "user_ref": user["_id"],
        "username": session.get("username", ""),
        "mobile": session.get("mobile", ""),
        "full_name": session.get("full_name", ""),
        "type": "deposit",
        "amount": float(session["amount"]),
        "method": "upi_qr",
        "reference": clean_reference,
        "qr_reference": clean_reference,
        "upi_id": session.get("upi_id", ""),
        "status": "pending",
        "currency": "INR",
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = db.wallet_transactions.insert_one(transaction)
        transaction["_id"] = result.inserted_id
        db.deposit_payment_sessions.update_one(
            {"_id": session["_id"], "status": "submitting"},
            {"$set": {"status": "submitted", "transaction_ref": result.inserted_id, "submitted_at": now, "updated_at": now}},
        )
    except Exception:
        db.deposit_payment_sessions.update_one(
            {"_id": session["_id"], "status": "submitting"},
            {"$set": {"status": "created", "updated_at": utcnow()}},
        )
        raise

    db.notifications.insert_one({
        "client_id": session["client_id"],
        "user_id": canonical_user_id,
        "title": "Deposit request submitted",
        "text": "Deposit request submitted. Admin will update it in a few minutes.",
        "type": "deposit",
        "read": False,
        "created_at": now,
    })
    return serialize(transaction)


def list_notifications(db, user_id: str, page: int, limit: int) -> dict:
    query = {"user_id": user_id}
    total = db.notifications.count_documents(query)
    unread = db.notifications.count_documents({**query, "read": {"$ne": True}})
    rows = list(db.notifications.find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).skip((page - 1) * limit).limit(limit))
    return {"items": serialize(rows), "unread": unread, "page": page, "limit": limit, "total": total, "has_more": page * limit < total}


def mark_notifications_read(db, user_id: str) -> int:
    result = db.notifications.update_many({"user_id": user_id, "read": {"$ne": True}}, {"$set": {"read": True, "read_at": utcnow()}})
    return result.modified_count


def dashboard(db, user_id: str) -> dict | None:
    user = get_user(db, user_id)
    if not user:
        return None
    wallet = wallet_summary(db, user_id)
    transactions = list_transactions(db, user_id, 1, 5)
    bets = list_bets(db, user_id, 1, 5)
    open_tickets = db.support_tickets.count_documents({"user_id": user_id, "status": {"$in": ["open", "pending"]}})
    return {"profile": user, "wallet": wallet, "recent_transactions": transactions["items"], "recent_bets": bets["items"], "open_support_tickets": open_tickets}
