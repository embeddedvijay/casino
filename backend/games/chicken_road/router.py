from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from .service import advance, cash_out, config, history, start

router = APIRouter(prefix="/api/games/chicken-road", tags=["Chicken Road"])

class StartRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    amount: float
    difficulty: str = "easy"

class RoundRequest(BaseModel):
    round_id: str

@router.get("/config")
def get_config(): return config()

@router.post("/start")
def start_game(payload: StartRequest): return start(payload.user_id, payload.amount, payload.difficulty)

@router.post("/step")
def next_step(payload: RoundRequest): return advance(payload.round_id)

@router.post("/cash-out")
def take_win(payload: RoundRequest): return cash_out(payload.round_id)

@router.get("/history")
def get_history(user_id: str = Query(...), limit: int = Query(20, ge=1, le=100)): return history(user_id, limit)
