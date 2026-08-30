from __future__ import annotations

import os
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from database import db
from services.portal_service import (
    create_ticket,
    dashboard,
    get_user,
    list_bets,
    list_promotions,
    list_notifications,
    list_tickets,
    list_transactions,
    update_user,
    wallet_summary,
    create_wallet_request,
    create_deposit_qr,
    submit_deposit_qr,
    mark_notifications_read,
)

router = APIRouter(prefix="/api/portal", tags=["User Portal"])
security = HTTPBearer(auto_error=False)


class BankDetails(BaseModel):
    account_holder_name: str | None = Field(default=None, max_length=100)
    bank_name: str | None = Field(default=None, max_length=100)
    account_number: str | None = Field(default=None, max_length=34)
    ifsc_code: str | None = Field(default=None, max_length=20)
    branch_name: str | None = Field(default=None, max_length=100)


class UpiDetails(BaseModel):
    upi_id: str | None = Field(default=None, max_length=100)
    upi_mobile: str | None = Field(default=None, max_length=15)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    full_name: str | None = Field(default=None, min_length=2, max_length=80)
    email: str | None = Field(default=None, max_length=160)
    mobile: str | None = Field(default=None, min_length=8, max_length=20)
    avatar: str | None = Field(default=None, max_length=500)
    language: str | None = Field(default=None, max_length=20)
    bank_details: BankDetails | None = None
    upi_details: UpiDetails | None = None


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=150)
    message: str = Field(min_length=5, max_length=4000)
    category: Literal["account", "wallet", "game", "technical", "other"] = "other"


class WalletRequestCreate(BaseModel):
    amount: float = Field(gt=0, le=10_000_000)
    method: Literal["upi", "bank", "qr", "usdt"]
    reference: str | None = Field(default=None, max_length=120)


class WithdrawalRequestCreate(BaseModel):
    amount: float = Field(ge=500, le=50_000)
    method: Literal["upi", "bank"]
    reference: str = Field(min_length=3, max_length=120)


class DepositQrCreate(BaseModel):
    amount: float = Field(ge=500, le=10_000_000)


class DepositQrDone(BaseModel):
    reference: str = Field(min_length=8, max_length=80)


def resolve_user_id(
    user_id: str | None = Query(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        for collection_name in ("user_sessions", "sessions", "auth_sessions"):
            session = db[collection_name].find_one({
                "$or": [{"token": token}, {"access_token": token}],
                "status": {"$nin": ["revoked", "expired"]},
            })
            if session:
                resolved = session.get("user_id") or session.get("username") or session.get("user_name")
                if resolved:
                    return str(resolved)
    legacy_allowed = os.getenv("ALLOW_LEGACY_USER_ID", "true").lower() in {"1", "true", "yes"}
    if legacy_allowed and (x_user_id or user_id):
        return str(x_user_id or user_id)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User login required")


def require_user(user_id: str = Depends(resolve_user_id)) -> str:
    if not get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


@router.get("/profile")
def profile(user_id: str = Depends(require_user)):
    return {"success": True, "profile": get_user(db, user_id)}


@router.put("/profile")
def profile_update(payload: ProfileUpdate, user_id: str = Depends(require_user)):
    changes = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    profile_data = update_user(db, user_id, changes)
    return {"success": True, "message": "Profile updated", "profile": profile_data}


@router.get("/dashboard")
def portal_dashboard(user_id: str = Depends(require_user)):
    return {"success": True, "dashboard": dashboard(db, user_id)}


@router.get("/wallet")
def wallet(user_id: str = Depends(require_user)):
    return {"success": True, "wallet": wallet_summary(db, user_id)}


@router.get("/wallet/transactions")
def transactions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    kind: str | None = Query(default=None),
    user_id: str = Depends(require_user),
):
    return {"success": True, **list_transactions(db, user_id, page, limit, kind)}


@router.post("/wallet/deposits", status_code=201)
def deposit_create(payload: WalletRequestCreate, user_id: str = Depends(require_user)):
    if not payload.reference or len(payload.reference.strip()) < 6:
        raise HTTPException(status_code=422, detail="Valid transaction reference required")
    transaction = create_wallet_request(db, user_id, "deposit", payload.amount, payload.method, payload.reference)
    return {"success": True, "message": "Deposit submitted for review", "transaction": transaction}


@router.post("/wallet/deposits/qr")
def deposit_qr_create(payload: DepositQrCreate, user_id: str = Depends(require_user)):
    try:
        payment = create_deposit_qr(db, user_id, payload.amount)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"success": True, "payment": payment}


@router.post("/wallet/deposits/qr/done", status_code=201)
def deposit_qr_done(payload: DepositQrDone, user_id: str = Depends(require_user)):
    try:
        transaction = submit_deposit_qr(db, user_id, payload.reference)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "success": True,
        "message": "Deposit request submitted. Admin will update it in a few minutes.",
        "transaction": transaction,
    }


@router.post("/wallet/withdrawals", status_code=201)
def withdrawal_create(payload: WithdrawalRequestCreate, user_id: str = Depends(require_user)):
    try:
        transaction = create_wallet_request(db, user_id, "withdrawal", payload.amount, payload.method, payload.reference)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "success": True,
        "message": "Withdrawal request submitted. Amount is locked until admin review.",
        "transaction": transaction,
    }


@router.get("/bets/history")
def bet_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    game: str | None = Query(default=None),
    bet_status: str | None = Query(default=None, alias="status"),
    user_id: str = Depends(require_user),
):
    return {"success": True, **list_bets(db, user_id, page, limit, game, bet_status)}


@router.get("/promotions")
def promotions(_: str = Depends(require_user)):
    return {"success": True, "items": list_promotions(db,_)}


@router.post("/support/tickets", status_code=201)
def support_create(payload: TicketCreate, user_id: str = Depends(require_user)):
    ticket = create_ticket(db, user_id, payload.subject, payload.message, payload.category)
    return {"success": True, "message": "Support ticket created", "ticket": ticket}


@router.get("/support/tickets")
def support_list(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(require_user),
):
    return {"success": True, **list_tickets(db, user_id, page, limit)}


@router.get("/notifications")
def notifications(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=30, ge=1, le=100),
    user_id: str = Depends(require_user),
):
    return {"success": True, **list_notifications(db, user_id, page, limit)}


@router.post("/notifications/read-all")
def notifications_read_all(user_id: str = Depends(require_user)):
    return {"success": True, "updated": mark_notifications_read(db, user_id)}
