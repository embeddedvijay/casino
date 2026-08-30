from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from core.tenant import bind_request_identity,user_security

from . import manager
from .schemas import LuckyRaceBetRequest, LuckyRaceClearRequest


router = APIRouter(
    prefix="/api/games/lucky-race",
    tags=["Lucky Race"],
)


@router.get("/state")
def get_state():
    return manager.public_data()


@router.post("/bet")
async def place_bet(req: LuckyRaceBetRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return await manager.place_bet(req)


@router.post("/clear")
async def clear_bets(req: LuckyRaceClearRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return await manager.clear_bets(req)


async def lucky_race_socket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
