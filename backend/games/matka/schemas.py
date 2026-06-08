from pydantic import BaseModel


class MatkaBetRequest(BaseModel):
    user_id: str
    bet_type: str
    amount: float


class MatkaClearRequest(BaseModel):
    user_id: str

class MarketMessageRequest(BaseModel):
    client_id:str="demo"
    user_id:str="guest"
    message:str
    market_name:str
    time_key:str