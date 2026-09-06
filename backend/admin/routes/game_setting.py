from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from admin.dependencies import current_admin
from admin.services.game_settings import (
    get_casino_settings,
    get_matka_markets,
    save_casino_settings,
    save_casino_win_ratio,
    save_matka_markets,
)

router = APIRouter(tags=["Admin Game Settings"])


class MatkaMarketInput(BaseModel):
    key: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    enabled: bool
    open_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    close_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    days: int = Field(default=6, ge=0, le=6)


class MatkaMarketsUpdate(BaseModel):
    markets: list[MatkaMarketInput] = Field(min_length=1, max_length=50)


class CasinoWinRatioUpdate(BaseModel):
    casino_win_ratio: float = Field(ge=0, le=100)


class CasinoSettingsUpdate(BaseModel):
    casino_name: str = Field(min_length=2, max_length=100)
    casino_short_name: str = Field(min_length=2, max_length=30)
    telegram_admin_id: str = Field(default="", max_length=50)
    maintenance_mode: bool = False


@router.get("/api/admin/games/matka/markets")
async def read_matka_markets(admin: dict = Depends(current_admin)):
    return await get_matka_markets(admin["client_id"])


@router.put("/api/admin/games/matka/markets")
async def update_matka_markets(
    payload: MatkaMarketsUpdate,
    admin: dict = Depends(current_admin),
):
    market_keys = [market.key.upper() for market in payload.markets]

    if len(market_keys) != len(set(market_keys)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate Matka market found.",
        )

    for market in payload.markets:
        if market.open_time == market.close_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{market.name}: OP and CL time cannot be the same.",
            )

    try:
        return await save_matka_markets(
            admin["client_id"],
            [market.model_dump() for market in payload.markets],
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/api/admin/casino-settings")
async def read_casino_settings(admin: dict = Depends(current_admin)):
    return await get_casino_settings(admin["client_id"])


@router.put("/api/admin/casino-settings")
async def update_casino_settings(
    payload: CasinoSettingsUpdate,
    admin: dict = Depends(current_admin),
):
    return await save_casino_settings(
        admin["client_id"],
        payload.model_dump(),
    )


@router.patch("/api/admin/casino-settings/win-ratio")
async def update_casino_win_ratio(
    payload: CasinoWinRatioUpdate,
    admin: dict = Depends(current_admin),
):
    return await save_casino_win_ratio(
        admin["client_id"],
        payload.casino_win_ratio,
    )