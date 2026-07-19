from datetime import datetime, timezone


DEFAULT_GAMES = [
    {
        "key": "aviator",
        "name": "Aviator",
        "enabled": True,
        "min_bet": 10,
        "max_bet": 10000,
        "house_edge": 1,
        "max_multiplier": 100,
        "waiting_seconds": 10,
        "result_seconds": 5,
        "description": "Aviator multiplier game",
    },
    {
        "key": "dragon-tiger",
        "name": "Dragon Tiger",
        "enabled": True,
        "min_bet": 10,
        "max_bet": 10000,
        "house_edge": 1,
        "max_multiplier": 2,
        "waiting_seconds": 10,
        "result_seconds": 5,
        "description": "Dragon Tiger card game",
    },
    {
        "key": "lucky-race",
        "name": "Lucky Race",
        "enabled": True,
        "min_bet": 10,
        "max_bet": 10000,
        "house_edge": 1,
        "max_multiplier": 10,
        "waiting_seconds": 10,
        "result_seconds": 5,
        "description": "Lucky Race game",
    },
    {
        "key": "matka",
        "name": "Matka",
        "enabled": True,
        "min_bet": 10,
        "max_bet": 10000,
        "house_edge": 1,
        "max_multiplier": 100,
        "waiting_seconds": 10,
        "result_seconds": 5,
        "description": "Matka game",
    },
]


def ensure_game_settings(database, client_id: str) -> None:
    database.admin_game_settings.create_index(
        [("client_id", 1), ("key", 1)],
        unique=True,
    )

    now = datetime.now(timezone.utc)

    for game in DEFAULT_GAMES:
        database.admin_game_settings.update_one(
            {
                "client_id": client_id,
                "key": game["key"],
            },
            {
                "$setOnInsert": {
                    **game,
                    "client_id": client_id,
                    "created_at": now,
                    "updated_at": now,
                }
            },
            upsert=True,
        )


def clean_game(game: dict | None) -> dict | None:
    if not game:
        return None

    game.pop("_id", None)
    game.pop("client_id", None)
    game.pop("created_at", None)
    game.pop("updated_at", None)
    return game


def list_games(database, client_id: str) -> list[dict]:
    ensure_game_settings(database, client_id)
    games = database.admin_game_settings.find({"client_id": client_id}).sort("name", 1)
    return [clean_game(game) for game in games]


def get_game(database, client_id: str, game_key: str) -> dict | None:
    ensure_game_settings(database, client_id)
    game = database.admin_game_settings.find_one(
        {
            "client_id": client_id,
            "key": game_key,
        }
    )
    return clean_game(game)


def update_game(
    database,
    client_id: str,
    game_key: str,
    values: dict,
) -> dict | None:
    ensure_game_settings(database, client_id)
    values["updated_at"] = datetime.now(timezone.utc)

    result = database.admin_game_settings.update_one(
        {
            "client_id": client_id,
            "key": game_key,
        },
        {"$set": values},
    )

    if result.matched_count == 0:
        return None

    return get_game(database, client_id, game_key)