import datetime
import uuid

from bson import ObjectId

from core.casino import CasinoError, close_round, open_round, place_bet, settle_bet
from database import db

from .engine import create_round, deal_round


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def user_query(user_id,client_id="demo"):
    choices = [{"user_id": user_id}, {"username": user_id}, {"mobile": user_id}]
    if ObjectId.is_valid(user_id):
        choices.append({"_id": ObjectId(user_id)})
    return {"client_id":client_id,"$or": choices}


def wallet_balance(user_id,client_id="demo"):
    user = db.users.find_one(user_query(user_id,client_id), {"balance": 1, "wallet_balance": 1})
    return round(float((user or {}).get("balance", (user or {}).get("wallet_balance", 0)) or 0), 2)


def start(req):
    round_id = "AB-" + uuid.uuid4().hex[:12].upper()
    joker, deck = create_round()
    db.andar_bahar_rounds.insert_one({
        "client_id":req.client_id,"round_id": round_id, "user_id": req.user_id, "joker": joker, "deck": deck,
        "status": "choosing", "created_at": now(), "updated_at": now(),
    })
    return {"success": True, "round_id": round_id, "joker": joker, "balance": wallet_balance(req.user_id,req.client_id)}


def play(req):
    amount = round(float(req.amount), 2)
    row = db.andar_bahar_rounds.find_one_and_update(
        {"client_id":req.client_id,"round_id": req.round_id, "user_id": req.user_id, "status": "choosing"},
        {"$set": {"status": "betting", "updated_at": now()}},
    )
    if not row:
        return {"success": False, "message": "Round is no longer available"}
    round_id = row["round_id"]
    open_round("andar-bahar", round_id, {"user_id": req.user_id})
    try:
        saved = place_bet(
            game="andar-bahar",
            round_id=round_id,
            user_id=req.user_id,
            amount=amount,
            position_key=req.side,
            metadata={"side": req.side},
            client_id=req.client_id,
        )
    except CasinoError as exc:
        close_round("andar-bahar", round_id, {"cancelled": True, "reason": str(exc)})
        db.andar_bahar_rounds.update_one({"_id": row["_id"], "status": "betting"}, {"$set": {"status": "choosing", "updated_at": now()}})
        return {"success": False, "message": str(exc), "code": exc.code, "balance": wallet_balance(req.user_id,req.client_id)}
    except Exception:
        close_round("andar-bahar", round_id, {"cancelled": True, "reason": "bet_error"})
        db.andar_bahar_rounds.update_one(
            {"_id": row["_id"], "status": "betting"},
            {"$set": {"status": "choosing", "updated_at": now()}},
        )
        raise
    joker, deals, winner = deal_round(row["joker"], row["deck"])
    won = winner == req.side
    payout = round(amount * 2, 2) if won else 0.0
    settle_bet(saved["id"], payout, {"winner": winner})
    close_round("andar-bahar", round_id, {"winner": winner})
    db.andar_bahar_rounds.update_one({"_id": row["_id"]}, {"$set": {
        "side": req.side, "amount": amount, "deals": deals, "winner": winner,
        "won": won, "payout": payout, "status": "settled", "settled_at": now(), "updated_at": now(),
    }, "$unset": {"deck": ""}})
    return {
        "success": True, "round_id": round_id, "joker": joker, "deals": deals,
        "winner": winner, "won": won, "amount": amount, "payout": payout,
        "balance": wallet_balance(req.user_id,req.client_id),
        "message": f"YOU WON ₹{payout:,.2f}" if won else f"{winner.upper()} WINS",
    }
