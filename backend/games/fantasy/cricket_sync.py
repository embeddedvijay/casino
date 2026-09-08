"""All-match API-Cricket pipeline for Gold365.

Place this file at: games/fantasy/cricket_sync.py
It uses games.fantasy.cricket_normalizer.normalize_cricket_event.

Flow every 10 seconds:
  1. Fetch all fixture events + provider live list.
  2. Fetch a full get_events(event_key) payload for every live match.
  3. Fetch get_odds(event_key) for every live match.
  4. Parse every event through the same generic normalizer.
  5. Save raw payload and normalized state in MongoDB.

The frontend reads cricket_market_events. It must only show rows where
state.status is `live` or `upcoming`; completed rows remain stored for audit
and settlement but are not published to the lobby.
"""
from __future__ import annotations

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from database import db
from games.fantasy.cricket_normalizer import normalize_cricket_event
from games.fantasy.cricket_settlement import settle_completed_cricket_events

API_URL = "https://apiv2.api-cricket.com/cricket/"
SYNC_STATE_ID = "api_cricket"


def raw_db():
    """Use the real PyMongo database even if project db has a wrapper."""
    return getattr(db, "_raw", db)


def api_call(method: str, **params: Any) -> dict[str, Any]:
    """Return the complete provider response, never only `result`."""
    api_key = os.getenv("API_CRICKET_KEY", "").strip()
    if not api_key:
        raise RuntimeError("API_CRICKET_KEY is not configured")

    query = urlencode({"method": method, "APIkey": api_key, **params})
    request = Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": "curl/8.5.0", "Accept": "application/json, */*"},
    )
    try:
        # Keep a 10-second live feed responsive. A slow provider call must
        # fail this cycle rather than delaying every match for 15 seconds.
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", "replace").strip()[:300]
        raise RuntimeError(f"API-Cricket {method} HTTP {error.code}: {body or error.reason}") from error
    except URLError as error:
        raise RuntimeError(f"API-Cricket {method} network error: {error.reason}") from error

    if payload.get("success") != 1:
        raise RuntimeError(f"API-Cricket {method} error: {payload}")
    return payload


def event_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result", [])
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict) and item.get("event_key")]
    if isinstance(result, dict):
        return [item for item in result.values() if isinstance(item, dict) and item.get("event_key")]
    return []


def is_live(event: dict[str, Any]) -> bool:
    return normalize_cricket_event(event).get("status") == "live"


def match_odds(odds_payload: dict[str, Any], event_id: str) -> dict[str, Any]:
    """Documented response: result -> event_key -> market -> selection -> book."""
    result = odds_payload.get("result")
    if not isinstance(result, dict):
        return {}
    odds = result.get(str(event_id), {})
    return odds if isinstance(odds, dict) else {}


def fetch_one_event(event_id: str) -> dict[str, Any] | None:
    rows = event_rows(api_call("get_events", event_key=event_id))
    return next((row for row in rows if str(row.get("event_key")) == str(event_id)), None)


def fetch_one_odds(event_id: str) -> dict[str, Any]:
    return match_odds(api_call("get_odds", event_key=event_id), event_id)


def ensure_cricket_indexes() -> None:
    """Startup hook imported by main.py."""
    database = raw_db()
    database.cricket_market_events.create_index("event_id", unique=True)
    database.cricket_market_events.create_index([("state.status", 1), ("event_live", 1)])
    database.cricket_market_events.create_index("synced_at")
    database.cricket_provider_events_raw.create_index("event_id", unique=True)
    database.cricket_provider_odds_raw.create_index("event_id", unique=True)


def sync_cricket_feed() -> dict[str, Any]:
    database = raw_db()
    ensure_cricket_indexes()
    cycle_started = datetime.now(timezone.utc)
    today = cycle_started.date()
    lookback = int(os.getenv("CRICKET_LOOKBACK_DAYS", "1"))
    upcoming = int(os.getenv("CRICKET_UPCOMING_DAYS", "7"))
    start = str(today - timedelta(days=lookback))
    stop = str(today + timedelta(days=upcoming))

    # All scheduled/live/completed fixture rows in one common source map.
    # These independent provider calls run together. Previously they ran one
    # after another, so a 15-second delay in each call made the visible quote
    # 40+ seconds old despite CRICKET_SYNC_SECONDS=10.
    with ThreadPoolExecutor(max_workers=3) as pool:
        initial = {
            "events": pool.submit(api_call, "get_events", date_start=start, date_stop=stop),
            "live": pool.submit(api_call, "get_livescore"),
            "scheduled_odds": pool.submit(api_call, "get_odds", date_start=start, date_stop=stop),
        }
        events_payload = initial["events"].result()
        live_payload = initial["live"].result()
        scheduled_odds_payload = initial["scheduled_odds"].result()
    events = {str(row["event_key"]): row for row in event_rows(events_payload)}

    # Livescore can have newer event_live/status values. Keep its non-empty
    # fields, then fetch full match detail below for scorecard/comments/extra.
    live_ids: set[str] = set()
    for row in event_rows(live_payload):
        event_id = str(row["event_key"])
        live_ids.add(event_id)
        base = events.get(event_id, {})
        events[event_id] = {**base, **{key: value for key, value in row.items() if value not in (None, "", [], {})}}

    # Event list can also mark a match live when it is temporarily absent from
    # get_livescore. Every live candidate gets its own detailed provider call.
    live_ids |= {event_id for event_id, event in events.items() if is_live(event)}

    detail_events: dict[str, dict[str, Any]] = {}
    detail_odds: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    # Parallel only across independent matches. One match failure never blocks
    # the rest of the feed cycle.
    with ThreadPoolExecutor(max_workers=int(os.getenv("CRICKET_FETCH_WORKERS", "8"))) as pool:
        jobs = {}
        for event_id in live_ids:
            jobs[pool.submit(fetch_one_event, event_id)] = ("event", event_id)
            jobs[pool.submit(fetch_one_odds, event_id)] = ("odds", event_id)
        for job in as_completed(jobs):
            kind, event_id = jobs[job]
            try:
                value = job.result()
                if kind == "event" and value:
                    detail_events[event_id] = value
                elif kind == "odds":
                    # Empty dict is a valid provider response: no odds at this poll.
                    detail_odds[event_id] = value
            except Exception as error:
                errors.append(f"{kind}:{event_id}:{error}")

    # Freshness starts when this batch is actually ready to publish, not when
    # the network cycle started.
    now = datetime.now(timezone.utc)

    published_live = 0
    published_upcoming = 0
    published_completed = 0

    for event_id, list_event in events.items():
        # Detailed event wins because it contains current scorecard, `extra`,
        # commentary and exact current players.
        event = detail_events.get(event_id, list_event)
        state = normalize_cricket_event(event)
        status = state["status"]
        # Live odds use an event_key request every cycle. Upcoming fixtures use
        # the one date-range response from this same cycle.
        odds = detail_odds.get(event_id, {}) if status == "live" else match_odds(scheduled_odds_payload, event_id)
        odds_fresh = status in {"live", "upcoming"} and bool(odds)

        # Raw data: used for audit/debug/settlement. Normalized state: used by
        # all frontend pages. Both are written during the same feed cycle.
        database.cricket_provider_events_raw.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "payload": event, "fetched_at": now, "source": "api-cricket:get_events"}},
            upsert=True,
        )
        database.cricket_provider_odds_raw.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "payload": odds, "fetched_at": now, "source": "api-cricket:get_odds"}},
            upsert=True,
        )
        database.cricket_market_events.update_one(
            {"event_id": event_id},
            {"$set": {
                "event_id": event_id,
                "event": event,
                "state": state,
                "odds": odds,
                "has_odds": bool(odds),
                "odds_fresh": odds_fresh,
                "odds_updated_at": now if odds_fresh else None,
                "score_fetched_at": now,
                "event_live": status == "live",
                "event_date": str(event.get("event_date_start") or ""),
                "synced_at": now,
            }},
            upsert=True,
        )
        if status == "live":
            published_live += 1
        elif status == "upcoming":
            published_upcoming += 1
        else:
            published_completed += 1

    # The same provider event state is now in MongoDB, so completed bets can
    # be settled from the final winner/status without using frontend data.
    settlement = settle_completed_cricket_events()
    database.cricket_sync_state.update_one(
        {"_id": SYNC_STATE_ID},
        {"$set": {
            "source": "api-cricket",
            "last_sync_at": now,
            "cycle_started_at": cycle_started,
            "cycle_seconds": round((now - cycle_started).total_seconds(), 3),
            "interval_seconds": int(os.getenv("CRICKET_SYNC_SECONDS", "10")),
            "events_seen": len(events),
            "live_events": published_live,
            "upcoming_events": published_upcoming,
            "completed_events": published_completed,
            "settlement": settlement,
            "errors": errors[-20:],
        }},
        upsert=True,
    )
    return {"events": len(events), "live": published_live, "upcoming": published_upcoming, "completed": published_completed, "settlement": settlement, "errors": errors}


async def cricket_sync_loop() -> None:
    interval = max(10, int(os.getenv("CRICKET_SYNC_SECONDS", "10")))
    while True:
        try:
            result = await asyncio.to_thread(sync_cricket_feed)
            print(f"Cricket synced: all={result['events']} live={result['live']} upcoming={result['upcoming']} completed={result['completed']}")
        except Exception as error:
            print(f"Cricket sync failed: {error}")
        await asyncio.sleep(interval)
