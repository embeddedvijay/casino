from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Callable

from bson import ObjectId
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from database import db


DEFAULT_GAME_SETTINGS = {
    "aviator": {"enabled": True, "min_bet": 10.0, "max_bet": 100000.0},
    "dragon-tiger": {"enabled": True, "min_bet": 10.0, "max_bet": 100000.0},
    "lucky-race": {"enabled": True, "min_bet": 10.0, "max_bet": 100000.0},
    "matka": {"enabled": True, "min_bet": 10.0, "max_bet": 100000.0},
    "plinko": {"enabled": True, "min_bet": 10.0, "max_bet": 10000.0},
    "chicken-road": {"enabled": True, "min_bet": 50.0, "max_bet": 1000.0},
}

GAME_BET_COLLECTIONS = {
    "aviator": "aviator_bets",
    "dragon-tiger": "dragon_tiger_bets",
    "lucky-race": "lucky_race_bets",
    "teen-patti": "teen_patti_bets",
    "andar-bahar": "andar_bahar_bets",
}


class CasinoError(ValueError):
    def __init__(self, message: str, code: str = "casino_error"):
        super().__init__(message)
        self.code = code


def utcnow():
    return datetime.now(timezone.utc)


def _plain_db():
    return getattr(db, "_raw", db)


def _game_bet_collection(raw, game: str):
    name = GAME_BET_COLLECTIONS.get(game)
    return raw[name] if name else None


def ensure_casino_indexes() -> None:
    raw = _plain_db()
    raw.users.create_index(
        [("client_id", ASCENDING), ("username", ASCENDING)],
        unique=True,
        sparse=True,
        name="unique_client_username",
    )
    raw.users.create_index(
        [("client_id", ASCENDING), ("mobile", ASCENDING)],
        unique=True,
        sparse=True,
        name="unique_client_mobile",
    )
    raw.casino_bets.create_index(
        [("game", ASCENDING), ("round_id", ASCENDING), ("user_id", ASCENDING), ("position_key", ASCENDING)],
        unique=True,
        name="unique_game_round_user_position",
    )
    raw.casino_bets.create_index([("user_id", ASCENDING), ("created_at", -1)])
    raw.casino_bets.create_index(
        [("client_id", ASCENDING), ("user_id", ASCENDING), ("created_at", -1)],
        name="client_user_bets_latest",
    )
    raw.casino_rounds.create_index([("game", ASCENDING), ("round_id", ASCENDING)], unique=True)
    raw.wallet_transactions.create_index([("user_id", ASCENDING), ("created_at", -1)])
    raw.wallet_transactions.create_index(
        [("client_id", ASCENDING), ("user_id", ASCENDING), ("created_at", -1)],
        name="client_user_wallet_latest",
    )
    raw.game_settings.create_index([("client_id", ASCENDING), ("game", ASCENDING)], unique=True)
    for collection_name in GAME_BET_COLLECTIONS.values():
        raw[collection_name].create_index(
            [("client_id", ASCENDING), ("user_id", ASCENDING), ("created_at", -1)],
            name="client_user_bets_latest",
        )


def recover_interrupted_games() -> dict:
    """Refund unfinished real bets after a process crash, once, before loops start."""
    raw=_plain_db(); refunded=0; cancelled=0; now=utcnow()
    for bet in raw.casino_bets.find({"status":{"$in":["pending","active"]},"game":{"$ne":"cricket-market"}}):
        changed=raw.casino_bets.update_one(
            {"_id":bet["_id"],"status":{"$in":["pending","active"]}},
            {"$set":{"status":"cancelled","cancel_reason":"server_restart","cancelled_at":now,"updated_at":now}},
        )
        if not changed.modified_count: continue
        cancelled+=1
        if not bet.get("is_demo"):
            raw.users.update_one({"_id":bet["user_ref"]},{"$inc":{"balance":bet["amount"]},"$set":{"updated_at":now}})
            raw.wallet_transactions.insert_one({
                "user_id":bet["user_id"],"user_ref":bet["user_ref"],"client_id":bet.get("client_id","demo"),
                "type":"game_refund","game":bet["game"],"amount":bet["amount"],"reference_id":str(bet["_id"]),
                "round_id":bet["round_id"],"reason":"server_restart","created_at":now,
            })
            refunded+=1
    rounds=raw.casino_rounds.update_many({"status":"open"},{"$set":{"status":"aborted","abort_reason":"server_restart","updated_at":now}}).modified_count
    return {"cancelled_bets":cancelled,"refunded_bets":refunded,"aborted_rounds":rounds}


def user_query(user_id: str, client_id: str | None = None) -> dict:
    value = str(user_id or "").strip()
    if not value:
        raise CasinoError("User ID required", "user_required")
    options = [
        {"user_id": value}, {"username": value}, {"user_name": value},
        {"mobile": value},
    ]
    if ObjectId.is_valid(value):
        options.append({"_id": ObjectId(value)})
    query: dict = {"$or": options}
    if client_id:
        query = {"client_id": str(client_id), "$or": options}
    return query


def resolve_user(user_id: str, client_id: str | None = None) -> dict:
    user = _plain_db().users.find_one(user_query(user_id, client_id))
    if not user:
        raise CasinoError("User not found", "user_not_found")
    if user.get("status", "active") in {"blocked", "inactive", "suspended"}:
        raise CasinoError("User account is not active", "user_inactive")
    return user


def is_demo_user(user: dict) -> bool:
    return bool(
        user.get("is_demo")
        or user.get("role") == "demo"
        or str(user.get("username", "")).lower() in {"demo", "demo123"}
    )


def game_settings(game: str, client_id: str = "demo") -> dict:
    defaults = dict(DEFAULT_GAME_SETTINGS.get(game, {"enabled": True, "min_bet": 1.0, "max_bet": 100000.0}))
    saved = _plain_db().game_settings.find_one({"client_id": client_id, "game": game}, {"_id": 0}) or {}
    defaults.update(saved)
    client = _plain_db().clients.find_one({"client_id": client_id}, {"maintenance_mode": 1}) or {}
    defaults["maintenance_mode"] = bool(client.get("maintenance_mode", False))
    return defaults


def validate_bet(game: str, amount: float, user: dict) -> float:
    try:
        amount = round(float(amount), 2)
    except (TypeError, ValueError) as exc:
        raise CasinoError("Invalid bet amount", "invalid_amount") from exc
    if not math.isfinite(amount) or amount <= 0:
        raise CasinoError("Invalid bet amount", "invalid_amount")
    if is_demo_user(user):
        return amount
    settings = game_settings(game, user.get("client_id", "demo"))
    if settings.get("maintenance_mode"):
        raise CasinoError("Casino is under maintenance", "maintenance")
    if not settings.get("enabled", True):
        raise CasinoError("Game is disabled", "game_disabled")
    if amount < float(settings["min_bet"]) or amount > float(settings["max_bet"]):
        raise CasinoError(
            f"Bet must be between {settings['min_bet']:g} and {settings['max_bet']:g}",
            "bet_limit",
        )
    return amount


def wallet_balance(user: dict) -> float:
    return round(float(user.get("balance", 0) or 0), 2)


def place_bet(*, game: str, round_id: str, user_id: str, amount: float, position_key: str, metadata: dict | None = None, client_id: str | None = None) -> dict:
    raw = _plain_db()
    user = resolve_user(user_id, client_id)
    tenant_id = str(user.get("client_id") or client_id or "demo")
    canonical_user_id = str(user["_id"])
    amount = validate_bet(game, amount, user)
    now = utcnow()
    document = {
        "game": game, "round_id": str(round_id), "user_id": canonical_user_id,
        "requested_user_id": str(user_id), "user_ref": user["_id"], "client_id": tenant_id,
        "position_key": str(position_key), "amount": amount, "bet": amount,
        "status": "pending", "payout": 0.0, "profit": -amount,
        "is_demo": is_demo_user(user), "metadata": metadata or {},
        "created_at": now, "updated_at": now,
    }
    try:
        inserted = raw.casino_bets.insert_one(document)
    except DuplicateKeyError as exc:
        raise CasinoError("Bet already placed", "duplicate_bet") from exc
    detail_collection = _game_bet_collection(raw, game)
    if detail_collection is not None:
        detail_collection.replace_one(
            {"_id": inserted.inserted_id},
            {"_id": inserted.inserted_id, "casino_bet_id": str(inserted.inserted_id), **document},
            upsert=True,
        )

    if not document["is_demo"]:
        updated = raw.users.find_one_and_update(
            {"_id": user["_id"], "client_id": tenant_id, "balance": {"$gte": amount}, "status": {"$nin": ["blocked", "inactive", "suspended"]}},
            {"$inc": {"balance": -amount}, "$set": {"updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raw.casino_bets.delete_one({"_id": inserted.inserted_id, "status": "pending"})
            if detail_collection is not None:
                detail_collection.delete_one({"_id": inserted.inserted_id, "status": "pending"})
            raise CasinoError("Insufficient balance", "insufficient_balance")
        user = updated
        raw.wallet_transactions.insert_one({
            "user_id": canonical_user_id, "user_ref": user["_id"], "client_id": tenant_id,
            "type": "game_bet", "game": game, "amount": -amount,
            "reference_id": str(inserted.inserted_id), "round_id": str(round_id), "created_at": now,
        })

    raw.casino_bets.update_one({"_id": inserted.inserted_id, "status": "pending"}, {"$set": {"status": "active", "updated_at": now}})
    if detail_collection is not None:
        detail_collection.update_one({"_id": inserted.inserted_id, "status": "pending"}, {"$set": {"status": "active", "updated_at": now}})
    return {"id": str(inserted.inserted_id), **document, "status": "active", "balance": wallet_balance(user)}


def settle_bet(bet_id: str, payout: float, result: Any = None) -> dict | None:
    raw = _plain_db()
    if not ObjectId.is_valid(str(bet_id)):
        return None
    payout = max(0.0, round(float(payout), 2))
    now = utcnow()
    bet = raw.casino_bets.find_one_and_update(
        {"_id": ObjectId(str(bet_id)), "status": "active"},
        {"$set": {
            "status": "won" if payout > 0 else "lost", "payout": payout,
            "profit": round(payout, 2), "result": result,
            "settled_at": now, "updated_at": now,
        }},
        return_document=ReturnDocument.AFTER,
    )
    if not bet:
        return None
    bet["profit"] = round(payout - float(bet["amount"]), 2)
    raw.casino_bets.update_one({"_id": bet["_id"]}, {"$set": {"profit": bet["profit"]}})
    detail_collection = _game_bet_collection(raw, bet["game"])
    if detail_collection is not None:
        detail_collection.update_one({"_id": bet["_id"]}, {"$set": {
            "status": bet["status"], "payout": payout, "profit": bet["profit"],
            "result": result, "settled_at": now, "updated_at": now,
        }})
    if payout and not bet.get("is_demo"):
        user = raw.users.find_one_and_update(
            {"_id": bet["user_ref"], "client_id": bet.get("client_id", "demo")}, {"$inc": {"balance": payout}, "$set": {"updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        raw.wallet_transactions.insert_one({
            "user_id": bet["user_id"], "user_ref": bet["user_ref"], "client_id": bet.get("client_id", "demo"),
            "type": "game_win", "game": bet["game"], "amount": payout,
            "reference_id": str(bet["_id"]), "round_id": bet["round_id"], "created_at": now,
        })
        bet["balance"] = wallet_balance(user or {})
    else:
        user = raw.users.find_one({"_id": bet["user_ref"], "client_id": bet.get("client_id", "demo")}) or {}
        bet["balance"] = wallet_balance(user)
    return bet


def cancel_user_bets(game: str, round_id: str, user_id: str, client_id: str | None = None) -> int:
    raw = _plain_db()
    user = resolve_user(user_id, client_id)
    tenant_id = str(user.get("client_id") or client_id or "demo")
    bets = list(raw.casino_bets.find({"client_id": tenant_id, "game": game, "round_id": str(round_id), "user_ref": user["_id"], "status": "active"}))
    cancelled = 0
    for bet in bets:
        now = utcnow()
        changed = raw.casino_bets.update_one({"_id": bet["_id"], "status": "active"}, {"$set": {"status": "cancelled", "cancelled_at": now, "updated_at": now}})
        if not changed.modified_count:
            continue
        cancelled += 1
        detail_collection = _game_bet_collection(raw, game)
        if detail_collection is not None:
            detail_collection.update_one({"_id": bet["_id"]}, {"$set": {"status": "cancelled", "cancelled_at": now, "updated_at": now}})
        if not bet.get("is_demo"):
            raw.users.update_one({"_id": bet["user_ref"], "client_id": tenant_id}, {"$inc": {"balance": bet["amount"]}, "$set": {"updated_at": now}})
            raw.wallet_transactions.insert_one({
                "user_id": bet["user_id"], "user_ref": bet["user_ref"], "client_id": bet.get("client_id", "demo"),
                "type": "game_refund", "game": game, "amount": bet["amount"],
                "reference_id": str(bet["_id"]), "round_id": str(round_id), "created_at": now,
            })
    return cancelled


def open_round(game: str, round_id: str, public_state: dict | None = None) -> None:
    _plain_db().casino_rounds.update_one(
        {"game": game, "round_id": str(round_id)},
        {"$set": {"status": "open", "state": public_state or {}, "updated_at": utcnow()}, "$setOnInsert": {"created_at": utcnow()}},
        upsert=True,
    )


def close_round(game: str, round_id: str, result: Any) -> None:
    _plain_db().casino_rounds.update_one(
        {"game": game, "round_id": str(round_id)},
        {"$set": {"status": "settled", "result": result, "settled_at": utcnow(), "updated_at": utcnow()}},
        upsert=True,
    )


def bet_history(user_id: str, game: str | None = None, limit: int = 50, client_id: str | None = None) -> list[dict]:
    user = resolve_user(user_id, client_id)
    query = {"client_id": str(user.get("client_id") or client_id or "demo"), "user_ref": user["_id"]}
    if game:
        query["game"] = game
    records = []
    for row in _plain_db().casino_bets.find(query).sort("created_at", -1).limit(max(1, min(int(limit), 200))):
        row["id"] = str(row.pop("_id")); row.pop("user_ref", None)
        for key in ("created_at", "updated_at", "settled_at", "cancelled_at"):
            if row.get(key): row[key] = row[key].isoformat()
        records.append(row)
    return records
