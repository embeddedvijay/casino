import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from database import db
from games.fantasy.cricket_normalizer import normalize_cricket_event
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
        # A delayed provider response must not hold the whole live feed behind
        # one match.  The next 10-second cycle will retry it.
        with urlopen(request, timeout=max(3, int(os.getenv("CRICKET_HTTP_TIMEOUT", "6")))) as response:
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
    # Use the same status decision as the app.  This covers provider values
    # such as "Time Out", Tea and rain breaks, where event_live is sometimes
    # blank even though the innings and its odds are still running.
    return normalize_cricket_event(event).get("status") == "live"


def ensure_cricket_indexes():
    database = raw_db()
    database.cricket_market_events.create_index("event_id", unique=True)
    database.cricket_market_events.create_index([("event_date", 1), ("has_odds", 1), ("event_live", 1)])
    database.cricket_market_events.create_index("synced_at")
    database.cricket_provider_events_raw.create_index("event_id", unique=True)
    database.cricket_provider_odds_raw.create_index("event_id", unique=True)
    database.cricket_provider_snapshots.create_index([("event_id", 1), ("fetched_at", -1)])
    # Raw live snapshots are kept for diagnostics, then automatically removed.
    database.cricket_provider_snapshots.create_index(
        "fetched_at", expireAfterSeconds=int(os.getenv("CRICKET_RAW_RETENTION_SECONDS", "86400"))
    )


def sync_cricket_feed() -> dict:
    """Fetch one shared provider feed and store it once for every tenant."""
    cycle_started = time.monotonic()
    database = raw_db()
    today = datetime.utcnow().date()
    today_text = str(today)
    # Read the complete relevant fixture window.  The live feed alone is not
    # enough: a provider can omit a live match during a timeout/innings break.
    lookback_days = max(0, int(os.getenv("CRICKET_LOOKBACK_DAYS", "1")))
    upcoming_days = max(0, int(os.getenv("CRICKET_UPCOMING_DAYS", "7")))
    window_start = str(today - timedelta(days=lookback_days))
    window_stop = str(today + timedelta(days=upcoming_days))
    # A full seven-day fixture + date-odds read is comparatively slow and
    # changes rarely. Do it periodically, never on every live-score tick.
    # The fast path below is solely for live scorecard and odds updates.
    fixture_refresh_seconds = max(30, int(os.getenv("CRICKET_FIXTURE_REFRESH_SECONDS", "60")))
    previous_sync = database.cricket_sync_state.find_one({"_id": SYNC_STATE_ID}, {"fixtures_refreshed_at": 1}) or {}
    fixture_at = previous_sync.get("fixtures_refreshed_at")
    if isinstance(fixture_at, datetime) and fixture_at.tzinfo is not None:
        fixture_at = fixture_at.replace(tzinfo=None)
    refresh_fixtures = not isinstance(fixture_at, datetime) or (datetime.utcnow() - fixture_at).total_seconds() >= fixture_refresh_seconds
    date_odds = {}
    if refresh_fixtures:
        with ThreadPoolExecutor(max_workers=2) as executor:
            events_future = executor.submit(provider_call, "get_events", date_start=window_start, date_stop=window_stop)
            date_odds_future = executor.submit(provider_call, "get_odds", date_start=window_start, date_stop=window_stop)
            events = events_future.result() or []
            date_odds = date_odds_future.result() or {}
    else:
        # Reuse the raw fixture payload already stored in Mongo. It keeps the
        # lobby complete while avoiding a 116-match provider request each tick.
        events = [row["event"] for row in database.cricket_market_events.find({}, {"_id": 0, "event": 1}) if isinstance(row.get("event"), dict)]
    live = provider_call("get_livescore") or []
    merged = {str(item.get("event_key")): item for item in events if item.get("event_key")}
    # get_livescore is useful to mark a fixture live, but for some matches it
    # returns blank score/commentary fields. Do not let that sparse response
    # erase the detailed get_events payload used for scorecard and last balls.
    for live_event in live:
        event_id = str(live_event.get("event_key") or "")
        if not event_id:
            continue
        existing = merged.get(event_id, {})
        live_values = {key: value for key, value in live_event.items() if value not in (None, "", {}, [])}
        merged[event_id] = {**existing, **live_values}
    # A multi-day fixture can disappear from the live feed just after it
    # finishes.  Active customer bets must still receive one final lookup.
    active_event_ids = [str(item) for item in database.casino_bets.distinct(
        "metadata.provider_event_id", {"game": "cricket-market", "status": "active"}
    ) if item]
    missing_active_ids = [event_id for event_id in active_event_ids if event_id not in merged]
    # Include already-stored live events too. This closes the gap where one
    # provider list poll misses a match but the match is still running.
    stored_live_ids = {str(item) for item in database.cricket_market_events.distinct("event_id", {"event_live": True}) if item}
    # Refresh every live event by its own key: scores, overs, last balls and
    # scorecard must come from get_events(event_key), never a stale list row.
    live_ids = {event_id for event_id, event in merged.items() if event_is_live(event)}
    detail_ids = sorted(live_ids | stored_live_ids | set(missing_active_ids))
    # The two event-key calls are independent. Fetch the detailed scorecard
    # and the continuously changing odds in the same parallel fan-out for
    # every live match, then publish them together as one DB snapshot.
    individual_odds = {}
    if detail_ids:
        # One detail + one odds request per live event. Twenty workers lets
        # ten running matches finish in one provider-timeout window instead of
        # two serial batches.
        workers = max(2, int(os.getenv("CRICKET_LIVE_WORKERS", "20")))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for event_id in detail_ids:
                futures[executor.submit(provider_call, "get_events", event_key=event_id)] = ("event", event_id)
                futures[executor.submit(provider_call, "get_odds", event_key=event_id)] = ("odds", event_id)
            for future in as_completed(futures):
                kind, event_id = futures[future]
                try:
                    response = future.result() or {}
                    if kind == "odds":
                        if response:
                            individual_odds[event_id] = response.get(event_id, response) if isinstance(response, dict) else response
                        continue
                    candidates = response.values() if isinstance(response, dict) else response
                    for item in candidates:
                        if isinstance(item, dict) and str(item.get("event_key")) == event_id:
                            detailed_values = {key: value for key, value in item.items() if value not in (None, "", {}, [])}
                            merged[event_id] = {**merged.get(event_id, {}), **detailed_values}
                            break
                except Exception:
                    pass
    now = datetime.utcnow()
    # API-Cricket can return success=1 with no odds payload on a later poll.
    # Keep today's last verified market instead of clearing every client list.
    cached_rows = database.cricket_market_events.find(
        {"odds": {"$exists": True, "$ne": {}}},
        {"_id": 0, "event_id": 1, "odds": 1, "odds_updated_at": 1},
    )
    cached_odds = {str(row["event_id"]): row for row in cached_rows if row.get("odds")}
    stored = 0
    # Save every provider event. Live score visibility must never depend on an
    # odds response; odds only control whether a market can accept a bet.
    for event_id, event in merged.items():
        provider_odds = individual_odds.get(event_id) or (date_odds.get(event_id, {}) if isinstance(date_odds, dict) else {})
        previous = cached_odds.get(event_id, {})
        odds = provider_odds or previous.get("odds", {})
        odds_updated_at = now if provider_odds else previous.get("odds_updated_at")
        # Keep provider payloads for audit/debug and write only one stable
        # normalized state shape for every match consumed by the app.
        database.cricket_provider_events_raw.update_one(
            {"event_id": event_id}, {"$set": {"event_id": event_id, "payload": event, "fetched_at": now, "source": "api-cricket:get_events"}}, upsert=True,
        )
        if provider_odds:
            database.cricket_provider_odds_raw.update_one(
                {"event_id": event_id}, {"$set": {"event_id": event_id, "payload": provider_odds, "fetched_at": now, "source": "api-cricket:get_odds"}}, upsert=True,
            )
        database.cricket_market_events.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "event": event, "state": normalize_cricket_event(event), "odds": odds, "has_odds": bool(odds), "odds_fresh": bool(provider_odds), "odds_updated_at": odds_updated_at, "score_fetched_at": now, "event_date": str(event.get("event_date_start") or today_text), "event_live": event_is_live(event), "synced_at": now}},
            upsert=True,
        )
        # Keep a short-lived raw audit trail of each changing live payload.
        # This lets us prove exactly what provider score/odds were used when a
        # bet was accepted, without keeping unlimited data forever.
        if event_is_live(event):
            database.cricket_provider_snapshots.insert_one({
                "event_id": event_id, "fetched_at": now, "event": event,
                "odds": provider_odds, "source": "api-cricket",
            })
        if odds:
            stored += 1
    # Test/first-class matches can remain live for multiple days. Retain a
    # current live event even when its original start date is older than today.
    # Never remove a stored event while a customer still has an active bet on
    # it.  It may briefly have no odds, but it is required for final result
    # polling and for the customer's open-bet screen.
    database.cricket_market_events.delete_many({
        "event_date": {"$lt": str(today - timedelta(days=1))}, "event_live": {"$ne": True},
        "event_id": {"$nin": active_event_ids},
    })
    settlement = settle_completed_cricket_events()
    database.cricket_sync_state.update_one(
        {"_id": SYNC_STATE_ID},
        {"$set": {"source": "api-cricket", "version": "cricket-feed-v8", "last_sync_at": now, "events_seen": len(merged), "live_events": len(live_ids), "odds_available": stored, "window": {"start": window_start, "stop": window_stop}, "settlement": settlement, "cycle_seconds": round(time.monotonic() - cycle_started, 3), "target_seconds": int(os.getenv("CRICKET_SYNC_SECONDS", "5")), "fixture_refresh_seconds": fixture_refresh_seconds, "status": "ok", **({"fixtures_refreshed_at": now} if refresh_fixtures else {})}},
        upsert=True,
    )
    return {"events_seen": len(merged), "odds_available": stored, "settlement": settlement, "synced_at": now}


def sync_live_odds() -> dict:
    """Five-second odds-only pass; it never waits for fixture/score payloads."""
    database = raw_db()
    rows = list(database.cricket_market_events.find(
        {"event_live": True}, {"_id": 0, "event_id": 1}
    ))
    event_ids = [str(row.get("event_id")) for row in rows if row.get("event_id")]
    if not event_ids:
        return {"checked": 0, "updated": 0}
    results = {}
    workers = min(len(event_ids), max(2, int(os.getenv("CRICKET_ODDS_WORKERS", "12"))))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(provider_call, "get_odds", event_key=event_id): event_id for event_id in event_ids}
        for future in as_completed(futures):
            event_id = futures[future]
            try:
                response = future.result() or {}
                odds = response.get(event_id, response) if isinstance(response, dict) else response
                if odds:
                    results[event_id] = odds
            except Exception:
                pass
    now = datetime.utcnow()
    for event_id in event_ids:
        odds = results.get(event_id)
        if odds:
            database.cricket_market_events.update_one(
                {"event_id": event_id},
                {"$set": {"odds": odds, "has_odds": True, "odds_fresh": True, "odds_updated_at": now}},
            )
            database.cricket_provider_odds_raw.update_one(
                {"event_id": event_id},
                {"$set": {"event_id": event_id, "payload": odds, "fetched_at": now, "source": "api-cricket:get_odds"}},
                upsert=True,
            )
        else:
            # Keep the previous values visible as context but never accept a
            # bet against a provider quote that failed this refresh.
            database.cricket_market_events.update_one({"event_id": event_id}, {"$set": {"odds_fresh": False}})
    database.cricket_sync_state.update_one(
        {"_id": SYNC_STATE_ID},
        {"$set": {"last_odds_poll_at": now, "odds_poll_seconds": int(os.getenv("CRICKET_ODDS_SYNC_SECONDS", "5")), "odds_updated_matches": len(results)}},
        upsert=True,
    )
    return {"checked": len(event_ids), "updated": len(results)}


async def cricket_sync_loop(interval_seconds: int | None = None):
    interval = max(5, interval_seconds or int(os.getenv("CRICKET_SYNC_SECONDS", "5")))
    odds_interval = max(3, int(os.getenv("CRICKET_ODDS_SYNC_SECONDS", "5")))
    next_score_at, next_odds_at = 0.0, 0.0
    while True:
        tick = time.monotonic()
        try:
            if tick >= next_score_at:
                result = await asyncio.to_thread(sync_cricket_feed)
                print(f"🏏 Cricket feed synced | events={result['events_seen']} odds={result['odds_available']} settled={result['settlement']['settled']} voided={result['settlement']['voided']}")
                next_score_at = tick + interval
                next_odds_at = tick + odds_interval
            elif tick >= next_odds_at:
                result = await asyncio.to_thread(sync_live_odds)
                print(f"🏏 Cricket odds synced | checked={result['checked']} updated={result['updated']}")
                next_odds_at = tick + odds_interval
        except Exception as error:
            print(f"Cricket sync loop failed: {type(error).__name__}: {error}")
            next_odds_at = tick + odds_interval
        await asyncio.sleep(max(0.25, min(next_score_at, next_odds_at) - time.monotonic()))
