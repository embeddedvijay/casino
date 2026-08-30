from fastapi import APIRouter,Depends
from core.tenant import bind_request_identity,user_security

from .manager import play, start
from .schemas import AndarBaharPlayRequest, AndarBaharStartRequest


router = APIRouter(prefix="/api/games/andar-bahar", tags=["Andar Bahar"])


@router.post("/start")
def start_round(req: AndarBaharStartRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return start(req)


@router.post("/play")
def play_round(req: AndarBaharPlayRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return play(req)
