from datetime import datetime, timezone
from math import comb, exp
from secrets import SystemRandom

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import db


RNG = SystemRandom()
ALLOWED_ROWS = (8, 12, 16)
ALLOWED_RISKS = ("low", "medium", "high")
HOUSE_RTP = 0.96


def utcnow():
    return datetime.now(timezone.utc)


def user_query(user_id: str):
    value = str(user_id or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="User ID required")
    return {
        "$or": [
            {"user_id": value},
            {"username": value},
            {"user_name": value},
        ]
    }


def multiplier_table(rows: int, risk: str):
    profiles = {
        "low": (0.75, 2.15, 1.9),
        "medium": (0.43, 3.45, 2.0),
        "high": (0.16, 5.30, 2.2),
    }
    center, curve, power = profiles[risk]
    half = rows / 2
    raw = [
        center * exp(curve * (abs(index - half) / half) ** power)
        for index in range(rows + 1)
    ]
    probabilities = [comb(rows, index) / (2**rows) for index in range(rows + 1)]
    expected = sum(probability * value for probability, value in zip(probabilities, raw))
    scale = HOUSE_RTP / expected
    return [round(max(0.1, min(1000.0, value * scale)), 2) for value in raw]


def game_config():
    return {
        "success": True,
        "rows": list(ALLOWED_ROWS),
        "risks": list(ALLOWED_RISKS),
        "min_bet": 10,
        "max_bet": 10000,
        "rtp": HOUSE_RTP,
        "multipliers": {
            risk: {str(rows): multiplier_table(rows, risk) for rows in ALLOWED_ROWS}
            for risk in ALLOWED_RISKS
        },
    }


def play(user_id: str, amount: float, risk: str, rows: int):
    risk = str(risk or "").lower()
    if rows not in ALLOWED_ROWS:
        raise HTTPException(status_code=400, detail="Rows must be 8, 12 or 16")
    if risk not in ALLOWED_RISKS:
        raise HTTPException(status_code=400, detail="Risk must be low, medium or high")
    amount = round(float(amount), 2)
    if amount < 10 or amount > 10000:
        raise HTTPException(status_code=400, detail="Bet must be between 10 and 10000")

    query = user_query(user_id)
    now = utcnow()
    debit_query = {
        "$and": [
            query,
            {"balance": {"$gte": amount}},
            {"status": {"$nin": ["blocked", "inactive"]}},
        ]
    }
    user = db.users.find_one_and_update(
        debit_query,
        {"$inc": {"balance": -amount}, "$set": {"updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )
    if not user:
        existing = db.users.find_one(query)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=400, detail="Insufficient balance or account blocked")

    try:
        path = [RNG.randrange(2) for _ in range(rows)]
        slot = sum(path)
        multipliers = multiplier_table(rows, risk)
        multiplier = multipliers[slot]
        payout = round(amount * multiplier, 2)
        final_user = user
        if payout:
            final_user = db.users.find_one_and_update(
                {"_id": user["_id"]},
                {"$inc": {"balance": payout}, "$set": {"updated_at": now}},
                return_document=ReturnDocument.AFTER,
            )

        bet = {
            "user_id": str(user_id),
            "game": "plinko",
            "amount": amount,
            "bet": amount,
            "risk": risk,
            "rows": rows,
            "path": path,
            "slot": slot,
            "multiplier": multiplier,
            "payout": payout,
            "profit": round(payout - amount, 2),
            "result": "won" if payout > amount else "lost",
            "status": "settled",
            "created_at": now,
            "settled_at": now,
        }
        inserted = db.plinko_bets.insert_one(bet)
        db.wallet_transactions.insert_many([
            {
                "user_id": str(user_id), "type": "game_bet", "game": "plinko",
                "amount": -amount, "reference_id": str(inserted.inserted_id), "created_at": now,
            },
            {
                "user_id": str(user_id), "type": "game_win", "game": "plinko",
                "amount": payout, "reference_id": str(inserted.inserted_id), "created_at": now,
            },
        ])
        return {
            "success": True,
            "bet_id": str(inserted.inserted_id),
            "path": path,
            "slot": slot,
            "multipliers": multipliers,
            "multiplier": multiplier,
            "payout": payout,
            "profit": round(payout - amount, 2),
            "balance": round(float(final_user.get("balance", 0)), 2),
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.users.update_one({"_id": user["_id"]}, {"$inc": {"balance": amount}})
        raise HTTPException(status_code=500, detail="Plinko bet could not be completed") from exc


def history(user_id: str, limit: int = 20):
    limit = max(1, min(int(limit), 100))
    records = []
    for item in db.plinko_bets.find({"user_id": str(user_id)}).sort("created_at", -1).limit(limit):
        item["id"] = str(item.pop("_id"))
        for key in ("created_at", "settled_at"):
            if item.get(key):
                item[key] = item[key].isoformat()
        records.append(item)
    return {"success": True, "history": records}
