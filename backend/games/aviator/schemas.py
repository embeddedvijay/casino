from pydantic import BaseModel


class AviatorBetRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
    seat: int
    amount: float


class AviatorCashoutRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
    seat: int
