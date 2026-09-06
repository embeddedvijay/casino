import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from database import db
from games.fantasy.cricket_settlement import settle_completed_cricket_events


API_CRICKET_URL = "https://apiv2.api-cricket.com/cricket/"
SYNC_STATE_ID = "api_cricket"


def raw_db():
    return getattr(db, "_raw", db)


def provider_call(method: str, **params):
    key = os.getenv("API_CRICKET_KEY", "")
    if not key:
        return None
    query = urlencode({"method": method, "APIkey": key, **params})
    try:
        request = Request(f"{API_CRICKET_URL}?{query}", headers={"User-Agent": "Gold365CricketSync/1.0", "Accept": "application/json"})
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode())
        return payload.get("result") if payload.get("success") == 1 else None
    except Exception as error:
        print(f"API-Cricket sync {method} failed: {type(error).__name__}: {error}")
        return None


def odds_event_ids(payload):
    if isinstance(payload, dict):
        return {str(event_id) for event_id, odds in payload.items() if odds}
    if isinstance(payload, list):
        return {str(item.get("event_key")) for item in payload if isinstance(item, dict) and item.get("event_key")}
    return set()


def event_is_live(event: dict) -> bool:
    status = str(event.get("event_status") or "").strip().lower()
    if status in {"finished", "abandoned", "cancelled"}:
        return False
    return str(event.get("event_live")) == "1" or status in {"in progress", "live", "started", "innings break", "stumps"}


def ensure_cricket_indexes():
    database = raw_db()
    database.cricket_market_events.create_index("event_id", unique=True)
    database.cricket_market_events.create_index([("event_date", 1), ("has_odds", 1), ("event_live", 1)])
    database.cricket_market_events.create_index("synced_at")


def sync_cricket_feed() -> dict:
    """Fetch one shared provider feed and store it once for every tenant."""
    database = raw_db()
    today = datetime.utcnow().date()
    today_text = str(today)
    events = provider_call("get_events", date_start=today_text, date_stop=today_text) or []
    live = provider_call("get_livescore") or []
    merged = {str(item.get("event_key")): item for item in events if item.get("event_key")}
    merged.update({str(item.get("event_key")): item for item in live if item.get("event_key")})
    # A multi-day fixture can disappear from the live feed just after it
    # finishes.  Active customer bets must still receive one final lookup.
    active_event_ids = [str(item) for item in database.casino_bets.distinct(
        "metadata.provider_event_id", {"game": "cricket-market", "status": "active"}
    ) if item]
    missing_active_ids = [event_id for event_id in active_event_ids if event_id not in merged]
    if missing_active_ids:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(provider_call, "get_events", event_key=event_id): event_id for event_id in missing_active_ids}
            for future in as_completed(futures):
                event_id = futures[future]
                try:
                    response = future.result() or []
                    candidates = response.values() if isinstance(response, dict) else response
                    for item in candidates:
                        if isinstance(item, dict) and str(item.get("event_key")) == event_id:
                            merged[event_id] = item
                            break
                except Exception:
                    pass
    date_odds = provider_call("get_odds", date_start=today_text, date_stop=today_text) or {}
    available_ids = odds_event_ids(date_odds)
    live_ids = {str(item.get("event_key")) for item in live if item.get("event_key")}
    missing_live_ids = [event_id for event_id in live_ids if event_id not in available_ids]
    individual_odds = {}
    if missing_live_ids:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(provider_call, "get_odds", event_key=event_id): event_id for event_id in missing_live_ids}
            for future in as_completed(futures):
                event_id = futures[future]
                try:
                    odds = future.result() or {}
                    if odds:
                        available_ids.add(event_id)
                        individual_odds[event_id] = odds.get(event_id, odds)
                except Exception:
                    pass
    now = datetime.utcnow()
    # API-Cricket can return success=1 with no odds payload on a later poll.
    # Keep today's last verified market instead of clearing every client list.
    cached_rows = database.cricket_market_events.find(
        {"event_date": today_text, "odds": {"$exists": True, "$ne": {}}},
        {"_id": 0, "event_id": 1, "odds": 1},
    )
    cached_odds = {str(row["event_id"]): row["odds"] for row in cached_rows if row.get("odds")}
    stored = 0
    # Save every provider event. Live score visibility must never depend on an
    # odds response; odds only control whether a market can accept a bet.
    for event_id, event in merged.items():
        odds = individual_odds.get(event_id) or (date_odds.get(event_id, {}) if isinstance(date_odds, dict) else {}) or cached_odds.get(event_id, {})
        database.cricket_market_events.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "event": event, "odds": odds, "has_odds": bool(odds), "event_date": str(event.get("event_date_start") or today_text), "event_live": event_is_live(event), "synced_at": now}},
            upsert=True,
        )
        if odds:
            stored += 1
    # Test/first-class matches can remain live for multiple days. Retain a
    # current live event even when its original start date is older than today.
    database.cricket_market_events.delete_many({"event_date": {"$lt": str(today - timedelta(days=1))}, "event_live": {"$ne": True}})
    settlement = settle_completed_cricket_events()
    database.cricket_sync_state.update_one(
        {"_id": SYNC_STATE_ID},
        {"$set": {"source": "api-cricket", "last_sync_at": now, "events_seen": len(merged), "odds_available": stored, "settlement": settlement, "status": "ok"}},
        upsert=True,
    )
    return {"events_seen": len(merged), "odds_available": stored, "settlement": settlement, "synced_at": now}


async def cricket_sync_loop(interval_seconds: int | None = None):
    interval = interval_seconds or int(os.getenv("CRICKET_SYNC_SECONDS", "45"))
    while True:
        try:
            result = await asyncio.to_thread(sync_cricket_feed)
            print(f"🏏 Cricket feed synced | events={result['events_seen']} odds={result['odds_available']} settled={result['settlement']['settled']} voided={result['settlement']['voided']}")
        except Exception as error:
            print(f"Cricket sync loop failed: {type(error).__name__}: {error}")
        await asyncio.sleep(max(15, interval))
