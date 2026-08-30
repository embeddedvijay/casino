from pydantic import BaseModel


class MatkaBetRequest(BaseModel):
    client_id: str = "demo"
    user_id: str
    bet_type: str
    amount: float


class MatkaClearRequest(BaseModel):
    client_id: str = "demo"
    user_id: str

class MarketMessageRequest(BaseModel):
    client_id:str="demo"
    user_id:str="guest"
    message:str
    market_name:str
    time_key:str

class MarketConfirmRequest(BaseModel):
    client_id:str="demo"
    user_id:str="guest"
    market_name:str=""
    market:str=""
    time_key:str=""
    message:str
    server_response:str=""
