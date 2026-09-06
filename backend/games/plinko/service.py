from datetime import datetime, timezone
from math import comb, exp
from secrets import SystemRandom
import uuid

from fastapi import HTTPException
from database import db
from core.casino import CasinoError, cancel_user_bets, game_settings, place_bet, settle_bet


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
    settings=game_settings("plinko")
    return {
        "success": True,
        "rows": list(ALLOWED_ROWS),
        "risks": list(ALLOWED_RISKS),
        "min_bet": settings["min_bet"],
        "max_bet": settings["max_bet"],
        "enabled": settings["enabled"],
        "rtp": HOUSE_RTP,
        "multipliers": {
            risk: {str(rows): multiplier_table(rows, risk) for rows in ALLOWED_ROWS}
            for risk in ALLOWED_RISKS
        },
    }


def play(user_id: str, amount: float, risk: str, rows: int, client_id: str = "demo"):
    risk = str(risk or "").lower()
    if rows not in ALLOWED_ROWS:
        raise HTTPException(status_code=400, detail="Rows must be 8, 12 or 16")
    if risk not in ALLOWED_RISKS:
        raise HTTPException(status_code=400, detail="Risk must be low, medium or high")
    amount = round(float(amount), 2)
    round_id="PL-"+uuid.uuid4().hex
    saved=None
    try:
        saved=place_bet(game="plinko",round_id=round_id,user_id=user_id,amount=amount,position_key="drop",metadata={"risk":risk,"rows":rows},client_id=client_id)
        path = [RNG.randrange(2) for _ in range(rows)]
        slot = sum(path)
        multipliers = multiplier_table(rows, risk)
        multiplier = multipliers[slot]
        payout = round(amount * multiplier, 2)
        settled=settle_bet(saved["id"],payout,{"path":path,"slot":slot,"multiplier":multiplier})
        now=utcnow()

        bet = {
            "client_id": client_id,
            "user_id": saved["user_id"],
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
            "status": "settled", "casino_bet_id":saved["id"], "round_id":round_id,
            "created_at": now,
            "settled_at": now,
        }
        inserted = db.plinko_bets.insert_one(bet)
        return {
            "success": True,
            "bet_id": str(inserted.inserted_id),
            "path": path,
            "slot": slot,
            "multipliers": multipliers,
            "multiplier": multiplier,
            "payout": payout,
            "profit": round(payout - amount, 2),
            "balance": settled.get("balance",saved["balance"]) if settled else saved["balance"],
        }
    except CasinoError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        if saved:
            cancel_user_bets("plinko",round_id,user_id,client_id)
        raise HTTPException(status_code=500, detail="Plinko bet could not be completed") from exc


def history(user_id: str, limit: int = 20, client_id: str = "demo"):
    limit = max(1, min(int(limit), 100))
    records = []
    for item in db.plinko_bets.find({"client_id": client_id, "user_id": str(user_id)}).sort("created_at", -1).limit(limit):
        item["id"] = str(item.pop("_id"))
        for key in ("created_at", "settled_at"):
            if item.get(key):
                item[key] = item[key].isoformat()
        records.append(item)
    return {"success": True, "history": records}
