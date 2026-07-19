from datetime import datetime, timezone


def get_casino_settings(database, client_id: str) -> dict:
    client = database.clients.find_one(
        {"client_id": client_id},
        {
            "_id": 0,
            "casino_name": 1,
            "client_name": 1,
            "casino_short_name": 1,
            "telegram_admin_id": 1,
            "maintenance_mode": 1,
        },
    )

    if not client:
        return {
            "casino_name": "",
            "casino_short_name": "",
            "telegram_admin_id": "",
            "maintenance_mode": False,
        }

    return {
        "casino_name": client.get("casino_name") or client.get("client_name", ""),
        "casino_short_name": client.get("casino_short_name", ""),
        "telegram_admin_id": str(client.get("telegram_admin_id", "")),
        "maintenance_mode": bool(client.get("maintenance_mode", False)),
    }


def update_casino_settings(database, client_id: str, values: dict) -> dict:
    values["updated_at"] = datetime.now(timezone.utc)

    database.clients.update_one(
        {"client_id": client_id},
        {"$set": values},
    )

    return get_casino_settings(database, client_id)