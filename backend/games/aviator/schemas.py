from pydantic import BaseModel


class AviatorBetRequest(BaseModel):
    user_id: str
    seat: int
    amount: float


class AviatorCashoutRequest(BaseModel):
    user_id: str
    seat: int