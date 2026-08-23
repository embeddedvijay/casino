from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from .service import game_config, history, play


router = APIRouter(prefix="/api/games/plinko", tags=["Plinko"])


class PlinkoBet(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    amount: float
    risk: str = "medium"
    rows: int = 12


@router.get("/config")
def config_endpoint():
    return game_config()


@router.post("/bet")
def bet_endpoint(payload: PlinkoBet):
    return play(payload.user_id, payload.amount, payload.risk, payload.rows)


@router.get("/history")
def history_endpoint(user_id: str = Query(...), limit: int = Query(20, ge=1, le=100)):
    return history(user_id, limit)
