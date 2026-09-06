from fastapi import APIRouter, Depends

from admin.dependencies import current_admin
from admin.services.management_service import get_management_summary
from database import db

router = APIRouter(prefix="/api/admin/management", tags=["Admin Management"])


@router.get("/summary")
def management_summary(admin: dict = Depends(current_admin)):
    return get_management_summary(db, admin["client_id"])