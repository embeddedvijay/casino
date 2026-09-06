from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from admin.dependencies import current_admin
from admin.services.game_service import (
    get_game,
    list_games,
    update_game,
)
from database import db

router = APIRouter(prefix="/api/admin/games", tags=["Admin Games"])


class GameToggle(BaseModel):
    enabled: bool


class GameUpdate(BaseModel):
    key: str | None = None
    name: str = Field(min_length=2, max_length=100)
    enabled: bool = True
    min_bet: float = Field(ge=0)
    max_bet: float = Field(gt=0)
    house_edge: float = Field(ge=0, le=100)
    max_multiplier: float = Field(gt=0)
    waiting_seconds: int = Field(ge=0, le=3600)
    result_seconds: int = Field(ge=0, le=3600)
    description: str = Field(default="", max_length=1000)


@router.get("")
def read_games(admin: dict = Depends(current_admin)):
    return list_games(db, admin["client_id"])


@router.get("/{game_key}")
def read_game(game_key: str, admin: dict = Depends(current_admin)):
    game = get_game(db, admin["client_id"], game_key)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game


@router.patch("/{game_key}")
def toggle_game(
    game_key: str,
    payload: GameToggle,
    admin: dict = Depends(current_admin),
):
    game = update_game(
        db,
        admin["client_id"],
        game_key,
        {"enabled": payload.enabled},
    )

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game


@router.put("/{game_key}")
def save_game(
    game_key: str,
    payload: GameUpdate,
    admin: dict = Depends(current_admin),
):
    if payload.max_bet < payload.min_bet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum bet cannot be lower than minimum bet.",
        )

    values = payload.model_dump(exclude={"key"})
    game = update_game(db, admin["client_id"], game_key, values)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game