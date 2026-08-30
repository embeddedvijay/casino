import datetime
import uuid

from bson import ObjectId

from core.casino import CasinoError, cancel_user_bets, close_round, open_round, place_bet, settle_bet
from database import db

from .engine import choose_auto_action, evaluate, random_alias, shuffled_deck, winner_keys


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def user_query(user_id, client_id="demo"):
    choices = [{"user_id": user_id}, {"username": user_id}, {"mobile": user_id}]
    if ObjectId.is_valid(user_id):
        choices.append({"_id": ObjectId(user_id)})
    return {"client_id": client_id, "$or": choices}


def wallet_balance(user_id, client_id="demo"):
    user = db.users.find_one(user_query(user_id, client_id), {"balance": 1, "wallet_balance": 1})
    return round(float((user or {}).get("balance", (user or {}).get("wallet_balance", 0)) or 0), 2)


def history(user_id, client_id="demo"):
    rows = db.teen_patti_rounds.find(
        {"client_id": client_id, "user_id": user_id, "phase": "result"},
        {"winner_label": 1, "pot": 1, "won": 1},
    ).sort("created_at", -1).limit(8)
    return [{"winner": row.get("winner_label", ""), "pot": row.get("pot", 0), "won": bool(row.get("won"))} for row in rows]


def session(user_id, client_id="demo"):
    return {"success": True, "balance": wallet_balance(user_id, client_id), "history": history(user_id, client_id)}


def public_round(row, reveal=False):
    hands = row["hands"]
    result = {
        "success": True,
        "round_id": row["round_id"],
        "balance": wallet_balance(row["user_id"],row.get("client_id","demo")),
        "pot": row["pot"],
        "boot": row["boot"],
        "hands": {"user": hands["user"]},
        "active": row["active"],
        "seen": row["seen"],
        "chaals": row["chaals"],
        "phase": row["phase"],
        "winner": row.get("winner_label"),
        "message": row.get("message", ""),
        "players": row["players"],
        "history": history(row["user_id"],row.get("client_id","demo")),
    }
    if reveal or row["phase"] == "result":
        result["hands"].update({"auto1": hands["auto1"], "auto2": hands["auto2"]})
    return result


def deal(req):
    existing = db.teen_patti_rounds.find_one({"client_id":req.client_id,"user_id": req.user_id, "phase": {"$in": ["playing", "settling"]}})
    if existing:
        return public_round(existing)
    boot = round(float(req.boot), 2)
    round_id = "TP-" + uuid.uuid4().hex[:12].upper()
    open_round("teen-patti", round_id, {"user_id": req.user_id})
    try:
        saved = place_bet(
            game="teen-patti",
            round_id=round_id,
            user_id=req.user_id,
            amount=boot,
            position_key="boot",
            metadata={"action": "boot"},
            client_id=req.client_id,
        )
    except CasinoError as exc:
        close_round("teen-patti", round_id, {"cancelled": True, "reason": str(exc)})
        return {"success": False, "message": str(exc), "code": exc.code, "balance": wallet_balance(req.user_id,req.client_id)}
    except Exception:
        close_round("teen-patti", round_id, {"cancelled": True, "reason": "bet_error"})
        raise
    deck = shuffled_deck()
    row = {
        "client_id":req.client_id,"round_id": round_id,
        "user_id": req.user_id,
        "boot": boot,
        "pot": round(boot * 3, 2),
        "hands": {"user": deck[:3], "auto1": deck[3:6], "auto2": deck[6:9]},
        "players": {
            "auto1": {"name": random_alias(), "automated": True},
            "auto2": {"name": random_alias(), "automated": True},
        },
        "active": {"user": True, "auto1": True, "auto2": True},
        "seen": False,
        "chaals": 0,
        "phase": "playing",
        "bet_ids": [saved["id"]],
        "message": "PLAY BLIND OR SEE YOUR CARDS",
        "created_at": now(),
        "updated_at": now(),
    }
    try:
        db.teen_patti_rounds.insert_one(row)
    except Exception:
        cancel_user_bets("teen-patti", round_id, req.user_id,req.client_id)
        raise
    return public_round(row)


def finish(row):
    claimed = db.teen_patti_rounds.find_one_and_update(
        {"_id": row["_id"], "phase": "playing"},
        {"$set": {"phase": "settling", "updated_at": now()}},
    )
    if not claimed:
        current = db.teen_patti_rounds.find_one({"_id": row["_id"]})
        return public_round(current, reveal=True)
    winners = winner_keys(row["hands"], row["active"])
    share = round(float(row["pot"]) / len(winners), 2)
    payout = share if "user" in winners else 0.0
    labels = {"user": "YOU", "auto1": row["players"]["auto1"]["name"], "auto2": row["players"]["auto2"]["name"]}
    winner_label = " & ".join(labels[key] for key in winners)
    for index, bet_id in enumerate(row["bet_ids"]):
        settle_bet(bet_id, payout if index == 0 else 0.0, {"winner": winner_label})
    close_round("teen-patti", row["round_id"], {"winner": winner_label})
    message = f"YOU WON ₹{payout:,.2f}" if payout else f"{winner_label} WINS"
    db.teen_patti_rounds.update_one(
        {"_id": row["_id"]},
        {"$set": {
            "phase": "result", "winner_keys": winners, "winner_label": winner_label,
            "won": payout > 0, "payout": payout, "message": message,
            "settled_at": now(), "updated_at": now(),
        }},
    )
    return public_round(db.teen_patti_rounds.find_one({"_id": row["_id"]}), reveal=True)


def act(req):
    row = db.teen_patti_rounds.find_one({"client_id":req.client_id,"round_id": req.round_id, "user_id": req.user_id})
    if not row:
        return {"success": False, "message": "Round not found"}
    if row["phase"] != "playing":
        return public_round(row, reveal=True)
    if req.action == "see":
        _, hand_name = evaluate(row["hands"]["user"])
        db.teen_patti_rounds.update_one({"_id": row["_id"], "phase": "playing"}, {"$set": {"seen": True, "message": hand_name, "updated_at": now()}})
        return public_round(db.teen_patti_rounds.find_one({"_id": row["_id"]}))
    if req.action == "pack":
        row["active"]["user"] = False
        db.teen_patti_rounds.update_one({"_id": row["_id"], "phase": "playing"}, {"$set": {"active": row["active"], "updated_at": now()}})
        return finish(db.teen_patti_rounds.find_one({"_id": row["_id"]}))

    stake = round(float(row["boot"]) * (2 if row["seen"] else 1), 2)
    try:
        saved = place_bet(
            game="teen-patti",
            round_id=row["round_id"],
            user_id=req.user_id,
            amount=stake,
            position_key=f"{req.action}:{uuid.uuid4()}",
            metadata={"action": req.action},
            client_id=req.client_id,
        )
    except CasinoError as exc:
        return {"success": False, "message": str(exc), "code": exc.code, "balance": wallet_balance(req.user_id,req.client_id)}
    row["bet_ids"].append(saved["id"])
    row["pot"] = round(float(row["pot"]) + stake, 2)
    if req.action == "show":
        db.teen_patti_rounds.update_one({"_id": row["_id"]}, {"$set": {"bet_ids": row["bet_ids"], "pot": row["pot"], "message": "SHOWING CARDS...", "updated_at": now()}})
        return finish(db.teen_patti_rounds.find_one({"_id": row["_id"]}))

    row["chaals"] += 1
    for key in ("auto1", "auto2"):
        if not row["active"][key]:
            continue
        if choose_auto_action(row["hands"][key], row["chaals"]) == "pack":
            row["active"][key] = False
        else:
            row["pot"] = round(float(row["pot"]) + float(row["boot"]), 2)
    db.teen_patti_rounds.update_one(
        {"_id": row["_id"]},
        {"$set": {"bet_ids": row["bet_ids"], "pot": row["pot"], "chaals": row["chaals"], "active": row["active"], "message": "TABLE PLAYED • YOUR TURN", "updated_at": now()}},
    )
    current = db.teen_patti_rounds.find_one({"_id": row["_id"]})
    if sum(bool(value) for value in row["active"].values()) == 1 or row["chaals"] >= 3:
        return finish(current)
    return public_round(current)
