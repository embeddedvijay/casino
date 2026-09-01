from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from io import BytesIO
import re
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument
import qrcode

from games.matka.db_ops import MATKA_BETS_DB_NAME, myclient


BET_COLLECTIONS = (
    ("casino_bets", None),
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

GAME_ALIASES = {
    "car-roulet":"lucky-race","car-roulette":"lucky-race","lucky-race":"lucky-race",
    "luck-race":"lucky-race","aviator":"aviator","dragon-tiger":"dragon-tiger",
    "matka":"matka","teen-patti":"teen-patti","andar-bahar":"andar-bahar",
    "plinko":"plinko","chicken-road":"chicken-road",
}

WITHDRAWAL_MIN = 500.0
WITHDRAWAL_MAX = 50_000.0
WITHDRAWAL_DAILY_LIMIT = 5
WITHDRAWAL_TIMEZONE = ZoneInfo("Asia/Kolkata")
FINAL_BET_STATUSES = ["settled", "won", "lost", "completed", "complete", "success"]


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
    allowed = {"name", "full_name", "email", "mobile", "avatar", "language", "bank_details", "upi_details"}
    payload = {key: value for key, value in changes.items() if key in allowed and value is not None}
    for section in ("bank_details","upi_details"):
        if isinstance(payload.get(section),dict):
            payload[section]={key:str(value).strip() for key,value in payload[section].items() if value is not None}
    display_name=str(payload.get("full_name") or payload.get("name") or "").strip()
    if display_name:
        payload["name"]=display_name
        payload["full_name"]=display_name
    if payload:
        payload["updated_at"] = utcnow()
        db.users.update_one(user_query(user_id), {"$set": payload})
    return get_user(db, user_id)


def balance_for(user: dict) -> float:
    return float(user.get("balance", user.get("wallet_balance", 0)) or 0)


def transaction_query(db, user_id: str) -> dict:
    raw_user=db.users.find_one(user_query(user_id),{"_id":1,"client_id":1,"user_id":1,"username":1,"user_name":1,"mobile":1})
    if not raw_user:return {"_id":{"$exists":False}}
    values=canonical_user_values(raw_user,user_id)
    return {"client_id":str(raw_user.get("client_id") or "demo"),"$or":[{"user_id":{"$in":values}},{"username":{"$in":values}},{"user_name":{"$in":values}}]}


def canonical_user_values(user: dict, requested_user_id: str) -> list[str]:
    values = {
        str(requested_user_id),
        str(user.get("_id") or ""),
        str(user.get("user_id") or ""),
        str(user.get("username") or ""),
        str(user.get("user_name") or ""),
        str(user.get("mobile") or ""),
    }
    return [value for value in values if value]


def owner_query(values: list[str]) -> dict:
    return {"$or": [
        {"user_id": {"$in": values}},
        {"username": {"$in": values}},
        {"user_name": {"$in": values}},
        {"player_id": {"$in": values}},
        {"Contact": {"$in": values}},
    ]}


def india_day_bounds(now: datetime) -> tuple[str, datetime, datetime]:
    local_now = now.astimezone(WITHDRAWAL_TIMEZONE)
    local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    local_end = local_start + timedelta(days=1)
    return local_start.date().isoformat(), local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)


def withdrawal_eligibility(db, user_id: str) -> dict:
    raw_user = db.users.find_one(user_query(user_id), {"password": 0, "password_hash": 0, "salt": 0, "otp": 0})
    if not raw_user:
        raise ValueError("User not found")
    now = utcnow()
    values = canonical_user_values(raw_user, user_id)
    wallet_owner = {"client_id":str(raw_user.get("client_id") or "demo"),"$or": [{"user_id": {"$in": values}}, {"username": {"$in": values}}, {"user_name": {"$in": values}}]}

    last_withdrawal = db.wallet_transactions.find_one(
        {"$and": [wallet_owner, {"type": "withdrawal"}, {"status": {"$in": ["approved", "completed", "success"]}}]},
        sort=[("approved_at", DESCENDING), ("updated_at", DESCENDING), ("created_at", DESCENDING)],
    )
    turnover_from = (
        last_withdrawal.get("approved_at")
        or last_withdrawal.get("updated_at")
        or last_withdrawal.get("created_at")
        if last_withdrawal else datetime(1970, 1, 1, tzinfo=timezone.utc)
    )
    deposit_rows = list(db.wallet_transactions.aggregate([
        {"$match": {"$and": [
            wallet_owner,
            {"type": "deposit"},
            {"status": {"$in": ["approved", "completed", "success"]}},
            {"created_at": {"$gt": turnover_from}},
        ]}},
        {"$group": {"_id": None, "total": {"$sum": {"$abs": {"$ifNull": ["$amount", 0]}}}}},
    ]))
    required_turnover = round(float(deposit_rows[0]["total"] if deposit_rows else 0), 2)

    valid_play = 0.0
    if "casino_bets" in db.list_collection_names():
        bet_rows = list(db.casino_bets.aggregate([
            {"$match": {"$and": [
                owner_query(values),
                {"created_at": {"$gt": turnover_from}},
                {"$or": [
                    {"settled": True},
                    {"status": {"$in": FINAL_BET_STATUSES}},
                ]},
            ]}},
            {"$group": {"_id": None, "total": {"$sum": {"$abs": {"$ifNull": ["$amount", 0]}}}}},
        ]))
        valid_play += float(bet_rows[0]["total"] if bet_rows else 0)

    # Matka currently writes its debit to wallet_transactions rather than casino_bets.
    matka_rows = list(db.wallet_transactions.aggregate([
        {"$match": {"$and": [
            wallet_owner,
            {"type": "matka_bet"},
            {"status": {"$in": ["completed", "settled", "success"]}},
            {"created_at": {"$gt": turnover_from}},
        ]}},
        {"$group": {"_id": None, "total": {"$sum": {"$abs": {"$ifNull": ["$amount", 0]}}}}},
    ]))
    valid_play = round(valid_play + float(matka_rows[0]["total"] if matka_rows else 0), 2)

    day_key, day_start, day_end = india_day_bounds(now)
    used_today = db.wallet_transactions.count_documents({"$and": [
        wallet_owner,
        {"type": "withdrawal"},
        {"created_at": {"$gte": day_start, "$lt": day_end}},
        {"status": {"$nin": ["failed", "cancelled"]}},
    ]})
    pending = db.wallet_transactions.find_one({"$and": [
        wallet_owner,
        {"type": "withdrawal"},
        {"status": {"$in": ["pending", "processing"]}},
    ]}, {"_id": 1, "transaction_id": 1})
    remaining_turnover = round(max(0.0, required_turnover - valid_play), 2)
    return {
        "eligible": not pending and used_today < WITHDRAWAL_DAILY_LIMIT and remaining_turnover <= 0,
        "balance": balance_for(raw_user),
        "minimum": WITHDRAWAL_MIN,
        "maximum": WITHDRAWAL_MAX,
        "daily_limit": WITHDRAWAL_DAILY_LIMIT,
        "used_today": used_today,
        "remaining_today": max(0, WITHDRAWAL_DAILY_LIMIT - used_today),
        "pending": bool(pending),
        "required_turnover": required_turnover,
        "valid_play": valid_play,
        "remaining_turnover": remaining_turnover,
        "day": day_key,
    }


def list_transactions(db, user_id: str, page: int, limit: int, kind: str | None = None) -> dict:
    query = transaction_query(db, user_id)
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
    query = transaction_query(db, user_id)
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
    approved_withdrawal = list(db.wallet_transactions.aggregate([
        {"$match": {"$and": [query, {"type": "withdrawal"}, {"status": {"$in": ["approved", "completed", "success"]}}]}},
        {"$group": {"_id": None, "amount": {"$sum": {"$abs": {"$ifNull": ["$amount", 0]}}}}},
    ]))
    totals["withdrawal"] = float(approved_withdrawal[0]["amount"] or 0) if approved_withdrawal else 0
    summary = {
        "user_id": user.get("user_id", user_id),
        "balance": balance_for(user),
        "currency": user.get("currency", "INR"),
        "total_deposit": totals.get("deposit", 0),
        "total_withdrawal": totals.get("withdrawal", 0),
        "total_winnings": sum(
            totals.get(kind,0)
            for kind in ("win","winning","game_win","matka_win")
        ),
    }
    summary["withdrawal"] = withdrawal_eligibility(db, user_id)
    return summary


def bet_owner_query(values: list[str]) -> dict:
    object_ids = [ObjectId(value) for value in values if ObjectId.is_valid(value)]
    choices: list[dict] = [
        {"user_id": {"$in": values}},
        {"username": {"$in": values}},
        {"user_name": {"$in": values}},
        {"player_id": {"$in": values}},
        {"Contact": {"$in": values}},
    ]
    if object_ids:
        choices.extend([
            {"user_ref": {"$in": object_ids}},
            {"user_id": {"$in": object_ids}},
        ])
    return {"$or": choices}


def canonical_game(value: Any) -> str:
    key=re.sub(r"[^a-z0-9]+","-",str(value or "").strip().lower()).strip("-")
    return GAME_ALIASES.get(key,key)


def list_bets(db, user_id: str, page: int, limit: int, game: str | None = None, status: str | None = None) -> dict:
    raw_user = db.users.find_one(user_query(user_id), {
        "_id": 1, "client_id":1, "user_id": 1, "username": 1, "user_name": 1, "mobile": 1,
    })
    if not raw_user:
        return {"items": [], "page": page, "limit": limit, "total": 0, "has_more": False}
    def money(value: Any) -> float:
        try:
            return round(float(value or 0), 2)
        except (TypeError, ValueError):
            return 0.0

    values = canonical_user_values(raw_user, user_id)
    client_id = str(raw_user.get("client_id") or "demo")
    selected_game=canonical_game(game) if game and game!="all" else ""
    rows: list[dict] = []
    seen: set[str] = set()
    collections=list(BET_COLLECTIONS)
    known={name for name,_ in collections}
    for name in db.list_collection_names():
        if name.startswith("matka_bets.") and name not in known:
            collections.append((name,"matka"))
    for collection_name, default_game in collections:
        if collection_name not in db.list_collection_names():
            continue
        collection_game=canonical_game(default_game)
        if selected_game and collection_game and collection_game != selected_game:
            continue
        query: dict = {"$and":[{"client_id":client_id},bet_owner_query(values)]}
        if status and status != "all":
            query = {"$and": [query, {"status": {"$regex": f"^{status}$", "$options": "i"}}]}
        for row in db[collection_name].find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(500):
            item = serialize(row)
            row_game=canonical_game(item.get("game") or item.get("game_type") or default_game)
            item["game"]=row_game or "unknown"
            item["collection"] = collection_name
            if selected_game and item["game"]!=selected_game:
                continue
            identity = str(item.get("casino_bet_id") or item.get("_id") or item.get("bet_id") or item.get("round_id") or "")
            if identity in seen:
                continue
            seen.add(identity)
            rows.append(item)

    if not selected_game or selected_game == "matka":
        matka_db = myclient[MATKA_BETS_DB_NAME]
        for collection_name in matka_db.list_collection_names():
            if collection_name.startswith("system."):
                continue
            matka_query = {"$and": [
                {"$or": [{"client_id": client_id}, {"Client": client_id}, {"client": client_id}]},
                {"$or": [
                    {"user_id": {"$in": values}}, {"username": {"$in": values}},
                    {"user_name": {"$in": values}}, {"Contact": {"$in": values}},
                    {"player_id": {"$in": values}},
                ]},
            ]}
            for row in matka_db[collection_name].find(matka_query).limit(500):
                item = serialize(row)
                amount = money(item.get("amount", item.get("Total", item.get("total", 0))))
                payout = money(item.get("payout", item.get("Win_Amt", item.get("win_amount", item.get("Win", 0)))))
                raw_status = str(item.get("status") or item.get("Status") or "settled").lower()
                if status and status != "all" and raw_status != str(status).lower():
                    continue
                item["game"] = "matka"
                item["collection"] = f"{MATKA_BETS_DB_NAME}.{collection_name}"
                item["user_id"] = str(item.get("user_id") or item.get("Contact") or user_id)
                item["amount"] = amount
                item["payout"] = payout
                item["profit"] = round(payout - amount, 2)
                item["status"] = raw_status
                item["won"] = payout > 0
                market_key = str(item.get("market") or item.get("Market") or "").strip()
                market_upper = market_key.upper()
                if market_upper.endswith("_OP"):
                    market_name, market_side = market_key[:-3].replace("_", " ").title(), "Open"
                elif market_upper.endswith("_CL"):
                    market_name, market_side = market_key[:-3].replace("_", " ").title(), "Close"
                else:
                    market_name = market_key.replace("_", " ").title()
                    market_side = str(item.get("side") or item.get("Side") or "").title()
                item["market_name"] = market_name
                item["market_side"] = market_side
                item["market"] = f"{market_name} • {market_side}" if market_side else market_name
                item["created_at"] = item.get("created_at") or item.get("updated_at") or item.get("Date") or collection_name
                identity = f"matka:{collection_name}:{item.get('_id') or item.get('Play_ID') or item.get('id') or ''}"
                if identity in seen:
                    continue
                seen.add(identity)
                rows.append(item)
    rows.sort(key=lambda item: str(item.get("created_at", item.get("placed_at", ""))), reverse=True)
    total = len(rows)
    start = (page - 1) * limit
    return {"items": rows[start:start + limit], "page": page, "limit": limit, "total": total, "has_more": start + limit < total}


def list_promotions(db,user_id: str) -> list[dict]:
    now = utcnow()
    user=db.users.find_one(user_query(user_id),{"client_id":1}) or {}
    query = {
        "client_id":str(user.get("client_id") or "demo"),
        "status": {"$in": ["active", "Active", True]},
        "$and": [
            {"$or": [{"starts_at": {"$exists": False}}, {"starts_at": None}, {"starts_at": {"$lte": now}}]},
            {"$or": [{"ends_at": {"$exists": False}}, {"ends_at": None}, {"ends_at": {"$gte": now}}]},
        ],
    }
    return serialize(list(db.promotions.find(query).sort([("priority", DESCENDING), ("created_at", DESCENDING)])))


def create_ticket(db, user_id: str, subject: str, message: str, category: str) -> dict:
    user=db.users.find_one(user_query(user_id),{"_id":1,"client_id":1}) or {}
    document = {
        "ticket_id": f"TKT-{int(utcnow().timestamp() * 1000)}",
        "client_id":str(user.get("client_id") or "demo"),
        "user_id":str(user.get("_id") or user_id),
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
    user=db.users.find_one(user_query(user_id),{"_id":1,"client_id":1}) or {}
    query = {"client_id":str(user.get("client_id") or "demo"),"user_id":str(user.get("_id") or user_id)}
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
    raw_user = db.users.find_one(user_query(user_id), {"password": 0, "password_hash": 0, "salt": 0, "otp": 0})
    if not raw_user:
        raise ValueError("User not found")
    user = serialize(raw_user)
    amount = round(float(amount), 2)
    now = utcnow()
    prefix = "DPS" if request_type == "deposit" else "WDR"
    reservation_token = None
    if request_type == "withdrawal":
        if amount < WITHDRAWAL_MIN:
            raise ValueError(f"Minimum withdrawal is ₹{WITHDRAWAL_MIN:,.0f}")
        if amount > WITHDRAWAL_MAX:
            raise ValueError(f"Maximum withdrawal is ₹{WITHDRAWAL_MAX:,.0f} per request")
        eligibility = withdrawal_eligibility(db, user_id)
        if eligibility["pending"]:
            raise ValueError("One withdrawal is already pending. Please wait for the admin decision.")
        if eligibility["used_today"] >= WITHDRAWAL_DAILY_LIMIT:
            raise ValueError("Daily withdrawal limit reached. Maximum 5 withdrawals are allowed per day.")
        if eligibility["remaining_turnover"] > 0:
            raise ValueError(f"Play ₹{eligibility['remaining_turnover']:,.2f} more before withdrawal (1x deposit play required).")
        if amount > eligibility["balance"]:
            raise ValueError(f"Insufficient wallet balance. Available ₹{eligibility['balance']:,.2f}")

        reservation_token = f"WDR-{ObjectId()}"
        day_key, _, _ = india_day_bounds(now)
        update_query = {
            "_id": raw_user["_id"],
            "balance": {"$gte": amount},
            "$or": [
                {"withdrawal_pending_token": {"$exists": False}},
                {"withdrawal_pending_token": None},
                {"withdrawal_pending_token": ""},
            ],
            "$and": [{"$or": [
                {"withdrawal_day": {"$ne": day_key}},
                {"withdrawal_daily_count": {"$lt": WITHDRAWAL_DAILY_LIMIT}},
                {"withdrawal_daily_count": {"$exists": False}},
            ]}],
        }
        reserved = db.users.find_one_and_update(
            update_query,
            [{"$set": {
                "balance": {"$subtract": [{"$ifNull": ["$balance", 0]}, amount]},
                "withdrawal_pending_token": reservation_token,
                "withdrawal_day": day_key,
                "withdrawal_daily_count": {
                    "$cond": [
                        {"$eq": ["$withdrawal_day", day_key]},
                        {"$add": [{"$ifNull": ["$withdrawal_daily_count", 0]}, 1]},
                        1,
                    ]
                },
                "updated_at": now,
            }}],
            return_document=ReturnDocument.AFTER,
        )
        if not reserved:
            raise ValueError("Withdrawal could not be reserved. Check balance, pending request, or daily limit and try again.")
        user = serialize(reserved)
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
    if reservation_token:
        transaction.update({
            "client_id": raw_user.get("client_id"),
            "user_ref": raw_user["_id"],
            "reservation_token": reservation_token,
            "balance_reserved": True,
            "balance_before": round(balance_for(raw_user), 2),
            "balance_after": round(balance_for(user), 2),
            "turnover_snapshot": eligibility,
        })
    try:
        result = db.wallet_transactions.insert_one(transaction)
    except Exception:
        if reservation_token:
            db.users.update_one(
                {"_id": raw_user["_id"], "withdrawal_pending_token": reservation_token},
                {"$inc": {"balance": amount, "withdrawal_daily_count": -1}, "$unset": {"withdrawal_pending_token": ""}},
            )
        raise
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
    user=db.users.find_one(user_query(user_id),{"_id":1,"client_id":1}) or {}
    query = {"client_id":str(user.get("client_id") or "demo"),"user_id":str(user.get("_id") or user_id)}
    total = db.notifications.count_documents(query)
    unread = db.notifications.count_documents({**query, "read": {"$ne": True}})
    rows = list(db.notifications.find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).skip((page - 1) * limit).limit(limit))
    return {"items": serialize(rows), "unread": unread, "page": page, "limit": limit, "total": total, "has_more": page * limit < total}


def mark_notifications_read(db, user_id: str) -> int:
    user=db.users.find_one(user_query(user_id),{"_id":1,"client_id":1}) or {}
    result = db.notifications.update_many({"client_id":str(user.get("client_id") or "demo"),"user_id":str(user.get("_id") or user_id), "read": {"$ne": True}}, {"$set": {"read": True, "read_at": utcnow()}})
    return result.modified_count


def dashboard(db, user_id: str) -> dict | None:
    user = get_user(db, user_id)
    if not user:
        return None
    wallet = wallet_summary(db, user_id)
    transactions = list_transactions(db, user_id, 1, 5)
    bets = list_bets(db, user_id, 1, 5)
    open_tickets = db.support_tickets.count_documents({"client_id":str(user.get("client_id") or "demo"),"user_id":str(user.get("_id") or user_id), "status": {"$in": ["open", "pending"]}})
    return {"profile": user, "wallet": wallet, "recent_transactions": transactions["items"], "recent_bets": bets["items"], "open_support_tickets": open_tickets}
