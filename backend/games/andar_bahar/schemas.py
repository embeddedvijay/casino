from typing import Literal

from pydantic import BaseModel, Field


class AndarBaharPlayRequest(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
    round_id: str = Field(min_length=6, max_length=80)
    side: Literal["andar", "bahar"]
    amount: float = Field(ge=10, le=100000)


class AndarBaharStartRequest(BaseModel):
    client_id: str = "demo"
    user_id: str = Field(min_length=1, max_length=100)
