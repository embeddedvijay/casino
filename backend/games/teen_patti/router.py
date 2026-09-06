from fastapi import APIRouter,Depends
from core.tenant import bind_request_identity,query_identity,user_security

from .manager import act, deal, session
from .schemas import TeenPattiActionRequest, TeenPattiDealRequest


router = APIRouter(prefix="/api/games/teen-patti", tags=["Teen Patti"])


@router.get("/session")
def get_session(user_id: str,client_id: str="demo",credentials=Depends(user_security)):
    user_id,client_id=query_identity(user_id,client_id,credentials)
    return session(user_id,client_id)


@router.post("/deal")
def deal_round(req: TeenPattiDealRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return deal(req)


@router.post("/action")
def round_action(req: TeenPattiActionRequest,credentials=Depends(user_security)):
    bind_request_identity(req,credentials)
    return act(req)
