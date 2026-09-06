from admin.services.game_service import ensure_game_settings


def sum_amount(database, collection_name: str, query: dict) -> float:
    result = list(
        database[collection_name].aggregate(
            [
                {"$match": query},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
            ]
        )
    )

    return float(result[0]["total"]) if result else 0.0


def get_management_summary(database, client_id: str) -> dict:
    ensure_game_settings(database, client_id)
    base = {"client_id": client_id}

    return {
        "users": database.users.count_documents(base),
        "deposits": sum_amount(
            database,
            "deposits",
            {**base, "status": {"$in": ["approved", "completed", "success"]}},
        ),
        "withdrawals": sum_amount(
            database,
            "withdrawals",
            {**base, "status": {"$in": ["approved", "completed", "success"]}},
        ),
        "pending_deposits": database.deposits.count_documents(
            {**base, "status": "pending"}
        ),
        "pending_withdrawals": database.withdrawals.count_documents(
            {**base, "status": "pending"}
        ),
        "active_games": database.admin_game_settings.count_documents(
            {**base, "enabled": True}
        ),
    }
