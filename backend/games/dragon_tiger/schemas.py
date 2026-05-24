from pydantic import BaseModel


class DragonTigerBetRequest(BaseModel):
    user_id: str
    bet_type: str
    amount: float


class DragonTigerClearRequest(BaseModel):
    user_id: str