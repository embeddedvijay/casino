from fastapi import APIRouter, Depends, Query
from core.tenant import bind_request_identity,query_identity,user_security
from pydantic import BaseModel, Field

from .service import advance, cash_out, config, history, start

router = APIRouter(prefix="/api/games/chicken-road", tags=["Chicken Road"])

class StartRequest(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    amount: float
    difficulty: str = "easy"

class RoundRequest(BaseModel):
    round_id: str

@router.get("/config")
def get_config(): return config()

@router.post("/start")
def start_game(payload: StartRequest,credentials=Depends(user_security)):
    bind_request_identity(payload,credentials)
    return start(payload.user_id,payload.amount,payload.difficulty,payload.client_id)

@router.post("/step")
def next_step(payload: RoundRequest): return advance(payload.round_id)

@router.post("/cash-out")
def take_win(payload: RoundRequest): return cash_out(payload.round_id)

@router.get("/history")
def get_history(user_id: str = Query(...), client_id: str = Query("demo"), limit: int = Query(20, ge=1, le=100),credentials=Depends(user_security)):
    user_id,client_id=query_identity(user_id,client_id,credentials)
    return history(user_id,limit,client_id)
