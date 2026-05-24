from pydantic import BaseModel


class LuckyRaceBetRequest(BaseModel):
    user_id: str
    bet_type: str
    amount: float


class LuckyRaceClearRequest(BaseModel):
    user_id: str