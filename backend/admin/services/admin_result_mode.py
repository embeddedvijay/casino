from datetime import datetime

from pymongo import ReturnDocument

from database import db


SUPPORTED_GAMES = {"aviator", "dragon-tiger", "lucky-race"}


def _now():
    return datetime.utcnow()


def ensure_indexes():
    db.admin_result_modes.create_index(
        [("client_id", 1), ("game", 1)],
        unique=True,
        name="unique_admin_result_mode",
    )


def get_admin_result_mode(client_id: str, game: str) -> dict:
    ensure_indexes()
    saved = db.admin_result_modes.find_one(
        {"client_id": client_id, "game": game},
        {"_id": 0},
    ) or {}
    queue = saved.get("queue", [])
    return {
        "game": game,
        "enabled": bool(saved.get("enabled", False)),
        "queue": queue,
        "pending_count": len(queue),
        "updated_at": saved.get("updated_at"),
    }


def save_admin_result_mode(client_id: str, game: str, enabled: bool, queue: list) -> dict:
    ensure_indexes()
    now = _now()
    db.admin_result_modes.update_one(
        {"client_id": client_id, "game": game},
        {
            "$set": {
                "enabled": enabled,
                "queue": queue,
                "updated_at": now,
            },
            "$setOnInsert": {
                "client_id": client_id,
                "game": game,
                "created_at": now,
            },
        },
        upsert=True,
    )
    return get_admin_result_mode(client_id, game)


def consume_next_admin_result(game: str, client_id: str = "demo"):
    """Atomically remove and return the next admin-selected result."""
    previous = db.admin_result_modes.find_one_and_update(
        {
            "client_id": client_id,
            "game": game,
            "enabled": True,
            "queue.0": {"$exists": True},
        },
        {"$pop": {"queue": -1}, "$set": {"updated_at": _now()}},
        return_document=ReturnDocument.BEFORE,
    )
    if not previous:
        return None
    return previous["queue"][0]
