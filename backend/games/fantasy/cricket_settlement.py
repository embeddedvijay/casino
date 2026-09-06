"""Provider-result settlement for the cricket exchange markets.

Only final provider outcomes are used.  Ambiguous markets are voided/refunded
instead of guessing a winner, and every update is guarded by status=active so
the same bet can never be paid twice.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database import db
from core.casino import settle_bet


FINAL_STATUSES = {"finished", "completed", "complete", "result"}
VOID_STATUSES = {"cancelled", "abandoned", "no result", "no-result", "postponed"}


def raw_db():
    return getattr(db, "_raw", db)


def _text(value) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _team_aliases(team: str) -> set[str]:
    """Provider result strings sometimes shorten 'Australia Women' to 'AUS Women'."""
    words = _text(team).split()
    if not words:
        return set()
    aliases = {" ".join(words)}
    if len(words) > 1:
        aliases.add(f"{words[0][:3]} {' '.join(words[1:])}")
    return aliases


def _outcome_from_event(event: dict) -> dict | None:
    """Return a trusted final outcome, a void outcome, or None while pending."""
    status = _text(event.get("event_status"))
    details = " ".join(_text(event.get(key)) for key in (
        "event_status_info", "event_result", "event_final_result", "event_winner", "event_winner_team",
    ))
    if status in VOID_STATUSES or any(token in details for token in ("cancelled", "abandoned", "no result", "no-result", "postponed")):
        return {"state": "void", "reason": status or "provider_void"}
    if status not in FINAL_STATUSES:
        return None

    home = _text(event.get("event_home_team"))
    away = _text(event.get("event_away_team"))
    winner = _text(event.get("event_winner") or event.get("event_winner_team"))
    if winner in {"draw", "tie"} or " match tied" in f" {details}" or " match drawn" in f" {details}":
        return {"state": "settled", "winner": "draw", "provider_status": status}
    if winner == home:
        return {"state": "settled", "winner": "home", "provider_status": status}
    if winner == away:
        return {"state": "settled", "winner": "away", "provider_status": status}
    if "won" in details or "winner" in details:
        matches = {
            outcome for outcome, aliases in (("home", _team_aliases(home)), ("away", _team_aliases(away)))
            if any(alias and alias in details for alias in aliases)
        }
        if matches == {"home"}:
            return {"state": "settled", "winner": "home", "provider_status": status}
        if matches == {"away"}:
            return {"state": "settled", "winner": "away", "provider_status": status}
    # A provider can mark a fixture finished before its winner field arrives.
    # Keep bets active until a result can be mapped; never guess or refund a
    # legitimate finished market merely because one poll was incomplete.
    return None


def _selection_outcome(bet: dict, event: dict) -> str | None:
    selection = _text((bet.get("metadata") or {}).get("selection_key") or (bet.get("metadata") or {}).get("selection"))
    if selection in {"home", _text(event.get("event_home_team"))}:
        return "home"
    if selection in {"away", _text(event.get("event_away_team"))}:
        return "away"
    if selection == "draw":
        return "draw"
    return None


def _void_bet(bet: dict, result: dict) -> bool:
    database = raw_db()
    now = datetime.now(timezone.utc)
    changed = database.casino_bets.update_one(
        {"_id": bet["_id"], "status": "active"},
        {"$set": {"status": "cancelled", "cancel_reason": result["reason"], "result": result, "cancelled_at": now, "updated_at": now}},
    )
    if not changed.modified_count:
        return False
    if not bet.get("is_demo"):
        database.users.update_one(
            {"_id": bet["user_ref"], "client_id": bet.get("client_id", "demo")},
            {"$inc": {"balance": float(bet["amount"])}, "$set": {"updated_at": now}},
        )
        database.wallet_transactions.insert_one({
            "user_id": bet["user_id"], "user_ref": bet["user_ref"], "client_id": bet.get("client_id", "demo"),
            "type": "game_refund", "game": "cricket-market", "amount": float(bet["amount"]),
            "reference_id": str(bet["_id"]), "round_id": bet["round_id"], "reason": result["reason"], "created_at": now,
        })
    return True


def settle_cricket_event(event_id: str, event: dict) -> dict:
    """Settle every active bet for one API-Cricket event exactly once."""
    result = _outcome_from_event(event)
    if not result:
        return {"settled": 0, "voided": 0, "pending": True}
    database = raw_db()
    bets = list(database.casino_bets.find({
        "game": "cricket-market", "status": "active", "metadata.provider_event_id": str(event_id),
    }))
    settled = voided = 0
    for bet in bets:
        selection = _selection_outcome(bet, event)
        if result["state"] == "void" or not selection:
            if _void_bet(bet, {**result, "reason": result.get("reason", "unsupported_selection")}):
                voided += 1
            continue
        metadata = bet.get("metadata") or {}
        side = _text(metadata.get("side") or "back")
        stake = float(metadata.get("stake") or bet["amount"])
        odds = float(metadata.get("odds") or 0)
        selection_won = selection == result["winner"]
        if side == "back":
            payout = round(stake * odds, 2) if selection_won else 0.0
        elif side == "lay":
            # The lay liability was debited on placement.  A successful lay
            # receives the liability back plus the opposing stake.
            payout = round(float(bet["amount"]) + stake, 2) if not selection_won else 0.0
        else:
            if _void_bet(bet, {"state": "void", "reason": "unsupported_side"}):
                voided += 1
            continue
        if settle_bet(str(bet["_id"]), payout, {**result, "selection": selection, "side": side, "event_id": str(event_id)}):
            settled += 1
    return {"settled": settled, "voided": voided, "pending": False}


def settle_completed_cricket_events() -> dict:
    """Run after each shared provider sync; tenant separation stays in each bet."""
    database = raw_db()
    totals = {"events": 0, "settled": 0, "voided": 0}
    active_ids = database.casino_bets.distinct("metadata.provider_event_id", {"game": "cricket-market", "status": "active"})
    for event_id in active_ids:
        row = database.cricket_market_events.find_one({"event_id": str(event_id)}, {"_id": 0, "event": 1})
        if not row or not row.get("event"):
            continue
        outcome = settle_cricket_event(str(event_id), row["event"])
        if not outcome["pending"]:
            totals["events"] += 1
            totals["settled"] += outcome["settled"]
            totals["voided"] += outcome["voided"]
    return totals
