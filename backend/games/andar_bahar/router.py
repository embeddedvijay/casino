from fastapi import APIRouter

from .manager import play, start
from .schemas import AndarBaharPlayRequest, AndarBaharStartRequest


router = APIRouter(prefix="/api/games/andar-bahar", tags=["Andar Bahar"])


@router.post("/start")
def start_round(req: AndarBaharStartRequest):
    return start(req)


@router.post("/play")
def play_round(req: AndarBaharPlayRequest):
    return play(req)
