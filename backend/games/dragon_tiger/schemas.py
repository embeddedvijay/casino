from pydantic import BaseModel


class DragonTigerBetRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
    bet_type: str
    amount: float


class DragonTigerClearRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
