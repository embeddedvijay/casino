from fastapi import APIRouter, Depends, Query
from core.tenant import bind_request_identity,query_identity,user_security
from pydantic import BaseModel, Field

from .service import game_config, history, play


router = APIRouter(prefix="/api/games/plinko", tags=["Plinko"])


class PlinkoBet(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    amount: float
    risk: str = "medium"
    rows: int = 12


@router.get("/config")
def config_endpoint():
    return game_config()


@router.post("/bet")
def bet_endpoint(payload: PlinkoBet,credentials=Depends(user_security)):
    bind_request_identity(payload,credentials)
    return play(payload.user_id, payload.amount, payload.risk, payload.rows, payload.client_id)


@router.get("/history")
def history_endpoint(user_id: str = Query(...), client_id: str = Query("demo"), limit: int = Query(20, ge=1, le=100),credentials=Depends(user_security)):
    user_id,client_id=query_identity(user_id,client_id,credentials)
    return history(user_id, limit, client_id)
