from fastapi import APIRouter, Query

from core.casino import DEFAULT_GAME_SETTINGS, bet_history, game_settings

router = APIRouter(prefix="/api/casino", tags=["Casino Core"])


@router.get("/games")
def game_catalog(client_id: str = "demo"):
    return {
        "success": True,
        "games": [
            {"game": game, **game_settings(game, client_id)}
            for game in DEFAULT_GAME_SETTINGS
        ],
    }


@router.get("/bets/history")
def user_bet_history(
    user_id: str = Query(..., min_length=1),
    game: str | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    return {"success": True, "history": bet_history(user_id, game, limit)}
