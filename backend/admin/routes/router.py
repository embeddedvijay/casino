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

router=APIRouter(prefix="/admin",tags=["Casino Admin"])
security=HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username:str
    password:str


class ChangePasswordRequest(BaseModel):
    current_password:str
    new_password:str=Field(min_length=8,max_length=128)


def current_session(credentials:HTTPAuthorizationCredentials|None=Depends(security)):
    if not credentials or credentials.scheme.lower()!="bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Login required.")
    session=get_admin_from_token(db,credentials.credentials)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Session expired. Login again.")
    return session


@router.post("/login")
def login(payload:LoginRequest):
    admin=authenticate_admin(db,payload.username,payload.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password.")
    token=create_admin_session(db,admin["username"])
    must_change=bool(admin.get("must_change_password",False))
    return {"access_token":token,"token_type":"bearer","must_change_password":must_change,"admin":{"username":admin["username"],"must_change_password":must_change}}


@router.post("/change-password")
def change_password(payload:ChangePasswordRequest,session:dict=Depends(current_session)):
    try:
        change_admin_password(db,session["username"],payload.current_password,payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(exc)) from exc
    revoke_admin_session(db,session["token_hash"])
    new_token=create_admin_session(db,session["username"])
    return {"message":"Password changed successfully.","access_token":new_token,"token_type":"bearer","must_change_password":False}


@router.get("/me")
def me(session:dict=Depends(current_session)):
    admin=db.clients.find_one({"admin_username":session["username"]},{"_id":0,"password_hash":0,"password_salt":0})
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Admin not found.")
    return admin