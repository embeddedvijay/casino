from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel,Field

from database import db
from admin.services.auth_service import (
    authenticate_admin,
    change_admin_password,
    create_admin_session,
    ensure_default_admin,
    get_admin_from_token,
    revoke_admin_session,
)
from admin.services.game_service import (
    get_casino_settings,
    get_matka_markets,
    save_casino_settings,
    save_casino_win_ratio,
    save_matka_markets,
)

router=APIRouter(tags=["Casino Admin"])
security=HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username:str
    password:str


class ChangePasswordRequest(BaseModel):
    current_password:str
    new_password:str=Field(min_length=8,max_length=128)


class MatkaMarketInput(BaseModel):
    key:str=Field(min_length=2,max_length=50)
    name:str=Field(min_length=2,max_length=100)
    enabled:bool=True
    open_time:str=Field(default="09:00",pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    close_time:str=Field(default="23:00",pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    days:int=Field(default=6,ge=0,le=6)


class MatkaMarketsUpdate(BaseModel):
    markets:list[MatkaMarketInput]=Field(min_length=1,max_length=50)


class CasinoWinRatioUpdate(BaseModel):
    casino_win_ratio:float=Field(ge=0,le=100)


class CasinoSettingsUpdate(BaseModel):
    casino_name:str=Field(min_length=2,max_length=100)
    casino_short_name:str=Field(min_length=2,max_length=30)
    telegram_admin_id:str=Field(default="",max_length=50)
    maintenance_mode:bool=False


def current_session(credentials:HTTPAuthorizationCredentials|None=Depends(security)):
    if not credentials or credentials.scheme.lower()!="bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Login required.")
    session=get_admin_from_token(db,credentials.credentials)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Session expired. Login again.")
    return session


@router.post("/admin/login")
def login(payload:LoginRequest):
    admin=authenticate_admin(db,payload.username,payload.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password.")
    token=create_admin_session(db,admin["username"])
    must_change=bool(admin.get("must_change_password",False))
    return {"access_token":token,"token_type":"bearer","must_change_password":must_change,"admin":{"username":admin["username"],"must_change_password":must_change}}


@router.post("/admin/change-password")
def change_password(payload:ChangePasswordRequest,session:dict=Depends(current_session)):
    try:
        change_admin_password(db,session["username"],payload.current_password,payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(exc)) from exc
    revoke_admin_session(db,session["token_hash"])
    new_token=create_admin_session(db,session["username"])
    return {"message":"Password changed successfully.","access_token":new_token,"token_type":"bearer","must_change_password":False}


@router.get("/admin/me")
def me(session:dict=Depends(current_session)):
    admin=db.clients.find_one({"admin_username":session["username"]},{"_id":0,"password_hash":0,"password_salt":0})
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Admin not found.")
    return admin


@router.get("/api/admin/games/matka/markets")
async def read_matka_markets(session:dict=Depends(current_session)):
    return await get_matka_markets(session["client_id"])


@router.put("/api/admin/games/matka/markets")
async def update_matka_markets(payload:MatkaMarketsUpdate,session:dict=Depends(current_session)):
    market_keys=[market.key.upper() for market in payload.markets]
    if len(market_keys)!=len(set(market_keys)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Duplicate Matka market found.")
    for market in payload.markets:
        if market.open_time==market.close_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{market.name}: OP and CL time cannot be the same.")
    try:
        return await save_matka_markets(session["client_id"],[market.model_dump() for market in payload.markets])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(exc)) from exc


@router.get("/api/admin/casino-settings")
async def read_casino_settings(session:dict=Depends(current_session)):
    return await get_casino_settings(session["client_id"])


@router.put("/api/admin/casino-settings")
async def update_casino_settings(payload:CasinoSettingsUpdate,session:dict=Depends(current_session)):
    return await save_casino_settings(session["client_id"],payload.model_dump())


@router.patch("/api/admin/casino-settings/win-ratio")
async def update_casino_win_ratio(payload:CasinoWinRatioUpdate,session:dict=Depends(current_session)):
    return await save_casino_win_ratio(session["client_id"],payload.casino_win_ratio)