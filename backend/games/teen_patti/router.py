from fastapi import APIRouter

from .manager import act, deal, session
from .schemas import TeenPattiActionRequest, TeenPattiDealRequest


router = APIRouter(prefix="/api/games/teen-patti", tags=["Teen Patti"])


@router.get("/session")
def get_session(user_id: str):
    return session(user_id)


@router.post("/deal")
def deal_round(req: TeenPattiDealRequest):
    return deal(req)


@router.post("/action")
def round_action(req: TeenPattiActionRequest):
    return act(req)

