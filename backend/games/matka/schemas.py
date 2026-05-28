from pydantic import BaseModel


class MatkaBetRequest(BaseModel):
    user_id: str
    bet_type: str
    amount: float


class MatkaClearRequest(BaseModel):
    user_id: str