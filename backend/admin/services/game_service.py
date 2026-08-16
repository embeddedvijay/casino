from datetime import datetime, timezone

from database import db


DEFAULT_MATKA_MARKETS = [
    {"key": "SRIDEVI_DAY", "name": "SRIDEVI DAY"},
    {"key": "SRIDEVI_NIGHT", "name": "SRIDEVI NIGHT"},
    {"key": "TIME_BAZAR_DAY", "name": "TIME BAZAR DAY"},
    {"key": "MAIN_BAZAR_NIGHT", "name": "MAIN BAZAR NIGHT"},
    {"key": "MADHUR_DAY", "name": "MADHUR DAY"},
    {"key": "MADHUR_NIGHT", "name": "MADHUR NIGHT"},
    {"key": "MILAN_DAY", "name": "MILAN DAY"},
    {"key": "MILAN_NIGHT", "name": "MILAN NIGHT"},
    {"key": "RAJDHANI_DAY", "name": "RAJDHANI DAY"},
    {"key": "RAJDHANI_NIGHT", "name": "RAJDHANI NIGHT"},
    {"key": "SUPREME_DAY", "name": "SUPREME DAY"},
    {"key": "SUPREME_NIGHT", "name": "SUPREME NIGHT"},
    {"key": "KALYAN_DAY", "name": "KALYAN DAY"},
    {"key": "KALYAN_NIGHT", "name": "KALYAN NIGHT"},
]

ALLOWED_MARKET_KEYS = {market["key"] for market in DEFAULT_MATKA_MARKETS}
DAYS_MIN = 0
DAYS_MAX = 6
DEFAULT_DAYS = 6


def utc_now():
    return datetime.now(timezone.utc)


def ensure_default_matka_markets(client_id: str) -> None:
    db["matka_markets"].create_index(
        [("client_id", 1), ("key", 1)],
        unique=True,
    )
    db["matka_timings"].create_index(
        [("client_id", 1), ("key", 1)],
        unique=True,
    )

    now = utc_now()

    for market in DEFAULT_MATKA_MARKETS:
        db["matka_markets"].update_one(
            {"client_id": client_id, "key": market["key"]},
            {
                "$setOnInsert": {
                    "client_id": client_id,
                    "key": market["key"],
                    "name": market["name"],
                    "enabled": True,
                    "status": "Active",
                    "days": DEFAULT_DAYS,
                    "created_at": now,
                    "updated_at": now,
                }
            },
            upsert=True,
        )
        db["matka_timings"].update_one(
            {"client_id": client_id, "key": market["key"]},
            {
                "$setOnInsert": {
                    "client_id": client_id,
                    "key": market["key"],
                    "open_time": "09:00",
                    "close_time": "23:00",
                    "created_at": now,
                    "updated_at": now,
                }
            },
            upsert=True,
        )


async def get_matka_markets(client_id: str) -> list[dict]:
    ensure_default_matka_markets(client_id)

    market_documents = {
        market["key"]: market
        for market in db["matka_markets"].find(
            {"client_id": client_id},
            {"_id": 0},
        )
    }
    timing_documents = {
        timing["key"]: timing
        for timing in db["matka_timings"].find(
            {"client_id": client_id},
            {"_id": 0},
        )
    }

    result = []

    for default_market in DEFAULT_MATKA_MARKETS:
        market = market_documents.get(default_market["key"], {})
        timing = timing_documents.get(default_market["key"], {})

        try:
            days = int(market.get("days", DEFAULT_DAYS))
        except (TypeError, ValueError):
            days = DEFAULT_DAYS

        result.append(
            {
                "key": default_market["key"],
                "name": market.get("name", default_market["name"]),
                "enabled": market.get(
                    "enabled",
                    market.get("status", "Active") == "Active",
                ),
                "open_time": timing.get("open_time", "09:00"),
                "close_time": timing.get("close_time", "23:00"),
                "days": min(DAYS_MAX, max(DAYS_MIN, days)),
            }
        )

    return result


async def save_matka_markets(client_id: str, markets: list[dict]) -> list[dict]:
    ensure_default_matka_markets(client_id)
    now = utc_now()

    for market in markets:
        market_key = market["key"].upper()

        if market_key not in ALLOWED_MARKET_KEYS:
            raise ValueError(f"Invalid Matka market: {market_key}")

        enabled = bool(market.get("enabled", True))
        try:
            days = int(market.get("days", DEFAULT_DAYS))
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{market['name']}: days must be a number between 0 and 6."
            ) from error

        if not DAYS_MIN <= days <= DAYS_MAX:
            raise ValueError(f"{market['name']}: days must be between 0 and 6.")

        db["matka_markets"].update_one(
            {"client_id": client_id, "key": market_key},
            {
                "$set": {
                    "name": market["name"],
                    "enabled": enabled,
                    "status": "Active" if enabled else "Inactive",
                    "days": days,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "client_id": client_id,
                    "key": market_key,
                    "created_at": now,
                },
            },
            upsert=True,
        )
        db["matka_timings"].update_one(
            {"client_id": client_id, "key": market_key},
            {
                "$set": {
                    "open_time": market["open_time"],
                    "close_time": market["close_time"],
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "client_id": client_id,
                    "key": market_key,
                    "created_at": now,
                },
            },
            upsert=True,
        )

    return await get_matka_markets(client_id)


async def get_casino_settings(client_id: str) -> dict:
    client = db["clients"].find_one(
        {"client_id": client_id},
        {
            "_id": 0,
            "casino_name": 1,
            "client_name": 1,
            "casino_short_name": 1,
            "telegram_admin_id": 1,
            "maintenance_mode": 1,
            "casino_win_ratio": 1,
        },
    ) or {}

    return {
        "casino_name": client.get("casino_name") or client.get("client_name", ""),
        "casino_short_name": client.get("casino_short_name", ""),
        "telegram_admin_id": str(client.get("telegram_admin_id", "")),
        "maintenance_mode": bool(client.get("maintenance_mode", False)),
        "casino_win_ratio": float(client.get("casino_win_ratio", 50)),
    }


async def save_casino_win_ratio(client_id: str, win_ratio: float) -> dict:
    db["clients"].update_one(
        {"client_id": client_id},
        {
            "$set": {
                "casino_win_ratio": float(win_ratio),
                "updated_at": utc_now(),
            }
        },
    )
    return await get_casino_settings(client_id)


async def save_casino_settings(client_id: str, values: dict) -> dict:
    values["updated_at"] = utc_now()
    db["clients"].update_one(
        {"client_id": client_id},
        {"$set": values},
    )
    return await get_casino_settings(client_id)