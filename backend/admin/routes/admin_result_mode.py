from datetime import datetime
from typing import Literal, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from admin.routes.router import current_session
from admin.services.admin_result_mode import (
    SUPPORTED_GAMES,
    get_admin_result_mode,
    save_admin_result_mode,
)
from games.car_roulet.engine import CARS


router = APIRouter(tags=["Admin Result Mode"])
LUCKY_RACE_KEYS = {car["key"] for car in CARS}


class AviatorResult(BaseModel):
    value: float = Field(ge=1.01, le=10000)


class DragonTigerResult(BaseModel):
    value: Literal["DRAGON", "TIGER", "TIE"]


class LuckyRaceResult(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def valid_car(cls, value):
        value = value.lower()
        if value not in LUCKY_RACE_KEYS:
            raise ValueError("Invalid Lucky Race car")
        return value


ResultItem = Union[AviatorResult, DragonTigerResult, LuckyRaceResult]


class AdminResultModeUpdate(BaseModel):
    enabled: bool
    results: list[dict] = Field(default_factory=list, max_length=5)


def validate_results(game: str, rows: list[dict]) -> list[dict]:
    if game == "aviator":
        return [AviatorResult.model_validate(row).model_dump() for row in rows]
    if game == "dragon-tiger":
        return [DragonTigerResult.model_validate(row).model_dump() for row in rows]
    if game == "lucky-race":
        return [LuckyRaceResult.model_validate(row).model_dump() for row in rows]
    raise HTTPException(status_code=404, detail="Game not supported for Admin Mode")


@router.get("/api/admin/result-mode/{game}")
def read_admin_result_mode(game: str, session: dict = Depends(current_session)):
    if game not in SUPPORTED_GAMES:
        raise HTTPException(status_code=404, detail="Game not supported for Admin Mode")
    return get_admin_result_mode(session["client_id"], game)


@router.put("/api/admin/result-mode/{game}")
def update_admin_result_mode(
    game: str,
    payload: AdminResultModeUpdate,
    session: dict = Depends(current_session),
):
    if game not in SUPPORTED_GAMES:
        raise HTTPException(status_code=404, detail="Game not supported for Admin Mode")
    try:
        queue = validate_results(game, payload.results)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if payload.enabled and len(queue) != 5:
        raise HTTPException(status_code=400, detail="Admin Mode requires exactly 5 results.")
    saved = save_admin_result_mode(session["client_id"], game, payload.enabled, queue)
    from database import db
    db.audit_logs.insert_one({
        "client_id": session["client_id"],
        "admin": session["username"],
        "action": "admin_result_mode_updated",
        "game": game,
        "enabled": payload.enabled,
        "pending_count": len(queue),
        "created_at": datetime.utcnow(),
    })
    return saved
