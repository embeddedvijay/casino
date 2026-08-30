from typing import Literal

from pydantic import BaseModel, Field


class TeenPattiDealRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    boot: float = Field(default=10, ge=10, le=1000)


class TeenPattiActionRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    round_id: str = Field(min_length=6, max_length=80)
    action: Literal["see", "pack", "chaal", "show"]

