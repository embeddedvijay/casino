from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from . import manager
from .schemas import DragonTigerBetRequest, DragonTigerClearRequest


router = APIRouter(
    prefix="/api/games/dragon-tiger",
    tags=["Dragon Tiger"],
)


@router.get("/state")
def get_state():
    return manager.public_data()


@router.post("/bet")
async def place_bet(req: DragonTigerBetRequest):
    return await manager.place_bet(req)


@router.post("/clear")
async def clear_bets(req: DragonTigerClearRequest):
    return await manager.clear_bets(req)


async def dragon_tiger_socket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)