from pydantic import BaseModel


class LuckyRaceBetRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
    bet_type: str
    amount: float


class LuckyRaceClearRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
