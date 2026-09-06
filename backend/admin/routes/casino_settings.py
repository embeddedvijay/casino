from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from admin.dependencies import current_admin
from admin.services.casino_settings_service import (
    get_casino_settings,
    update_casino_settings,
)
from database import db

router = APIRouter(prefix="/api/admin/casino-settings", tags=["Casino Settings"])


class CasinoSettingsUpdate(BaseModel):
    casino_name: str = Field(min_length=2, max_length=100)
    casino_short_name: str = Field(min_length=2, max_length=30)
    telegram_admin_id: str = Field(default="", max_length=50)
    maintenance_mode: bool = False


@router.get("")
def read_settings(admin: dict = Depends(current_admin)):
    return get_casino_settings(db, admin["client_id"])


@router.put("")
def save_settings(
    payload: CasinoSettingsUpdate,
    admin: dict = Depends(current_admin),
):
    return update_casino_settings(
        db,
        admin["client_id"],
        payload.model_dump(),
    )