import hashlib
import hmac
import os
import secrets
from datetime import datetime,timedelta,timezone


TOKEN_HOURS=int(os.getenv("ADMIN_TOKEN_HOURS","8"))
PBKDF2_ITERATIONS=310_000


def utc_now():
    return datetime.now(timezone.utc)


def password_hash(password:str,salt_hex:str)->str:
    return hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),PBKDF2_ITERATIONS).hex()


def new_password_record(password:str)->tuple[str,str]:
    salt=secrets.token_hex(16)
    return password_hash(password,salt),salt


def verify_password(password:str,stored_hash:str,salt:str)->bool:
    return hmac.compare_digest(password_hash(password,salt),stored_hash)


def validate_new_password(password:str):
    if len(password)<8:
        raise ValueError("New password must contain at least 8 characters.")
    if not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Password needs uppercase, lowercase and a number.")


def ensure_default_admin(database):
    database.clients.create_index("admin_username",unique=True,sparse=True)
    database.admin_sessions.create_index("expires_at",expireAfterSeconds=0)
    return True


def authenticate_admin(database,username:str,password:str):
    client=database.clients.find_one({"admin_username":username.strip(),"status":"active"})
    if not client or not verify_password(password,client["password_hash"],client["password_salt"]):
        return None
    return {"username":client["admin_username"],"client_id":client["client_id"],"must_change_password":bool(client.get("must_change_password",False))}


def token_hash(token:str)->str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_admin_session(database,username:str)->str:
    raw_token=secrets.token_urlsafe(48)
    database.admin_sessions.insert_one({"token_hash":token_hash(raw_token),"username":username,"created_at":utc_now(),"expires_at":utc_now()+timedelta(hours=TOKEN_HOURS)})
    return raw_token


def get_admin_from_token(database,token:str):
    hashed=token_hash(token)
    session=database.admin_sessions.find_one({"token_hash":hashed,"expires_at":{"$gt":utc_now()}})
    if not session:
        return None
    client=database.clients.find_one({"admin_username":session["username"],"status":"active"})
    if not client:
        return None
    return {"username":session["username"],"client_id":client["client_id"],"token_hash":hashed,"must_change_password":bool(client.get("must_change_password",False))}


def change_admin_password(database,username:str,current_password:str,new_password:str):
    client=database.clients.find_one({"admin_username":username,"status":"active"})
    if not client or not verify_password(current_password,client["password_hash"],client["password_salt"]):
        raise ValueError("Current password is incorrect.")
    if current_password==new_password:
        raise ValueError("New password must be different from the current password.")
    validate_new_password(new_password)
    hashed,salt=new_password_record(new_password)
    database.clients.update_one({"_id":client["_id"]},{"$set":{"password_hash":hashed,"password_salt":salt,"must_change_password":False,"updated_at":utc_now()}})


def revoke_admin_session(database,hashed_token:str):
    database.admin_sessions.delete_one({"token_hash":hashed_token})