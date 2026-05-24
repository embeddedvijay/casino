from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from . import manager
from .schemas import AviatorBetRequest, AviatorCashoutRequest


router = APIRouter(prefix="/api/games/aviator", tags=["Aviator"])


@router.get("/state")
def get_state():
    return manager.public_data()


@router.post("/bet")
async def place_bet(req: AviatorBetRequest):
    return await manager.place_bet(req)


@router.post("/cashout")
async def cashout(req: AviatorCashoutRequest):
    return await manager.cashout(req)


async def aviator_socket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)