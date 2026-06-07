from fastapi import APIRouter,HTTPException,Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from database import db

router=APIRouter(prefix="/auth",tags=["Auth Users"])

users_collection=db["users"]
clients_collection=db["clients"]
password_reset_collection=db["password_reset_requests"]

class CreateAccount(BaseModel):
    client_id:str
    full_name:str
    mobile:str
    password:str
    confirm_password:str

class LoginUser(BaseModel):
    client_id:str
    mobile:str
    password:str

class ForgotPassword(BaseModel):
    client_id:str
    name:str
    mobile:str

class UserUpdate(BaseModel):
    full_name:Optional[str]=None
    mobile:Optional[str]=None
    email:Optional[str]=None
    password:Optional[str]=None
    balance:Optional[float]=None
    status:Optional[str]=None

def check_client(client_id):
    client=clients_collection.find_one({"client_id":client_id})
    if not client:
        raise HTTPException(status_code=404,detail="Client not found")
    if client.get("status")!="active":
        raise HTTPException(status_code=403,detail="Client inactive")
    return client

def serialize_user(user):
    return {
        "id":str(user["_id"]),
        "client_id":user.get("client_id",""),
        "full_name":user.get("full_name",""),
        "username":user.get("username",""),
        "mobile":user.get("mobile",""),
        "email":user.get("email",""),
        "role":user.get("role","user"),
        "balance":user.get("balance",0),
        "status":user.get("status","active"),
        "is_demo":user.get("is_demo",False),
        "created_at":user.get("created_at"),
        "updated_at":user.get("updated_at")
    }

@router.post("/create-account")
def create_account(data:CreateAccount):
    check_client(data.client_id)
    if data.password!=data.confirm_password:
        raise HTTPException(status_code=400,detail="Password not matched")
    exists=users_collection.find_one({"client_id":data.client_id,"mobile":data.mobile})
    if exists:
        raise HTTPException(status_code=400,detail="Mobile number already registered")
    user={
        "client_id":data.client_id,
        "full_name":data.full_name,
        "username":data.mobile,
        "mobile":data.mobile,
        "password":data.password,
        "role":"user",
        "balance":0,
        "status":"active",
        "is_demo":False,
        "created_at":datetime.utcnow(),
        "updated_at":datetime.utcnow()
    }
    result=users_collection.insert_one(user)
    new_user=users_collection.find_one({"_id":result.inserted_id})
    return {"message":"Account created successfully","user":serialize_user(new_user)}

@router.post("/login")
def login(data:LoginUser):
    check_client(data.client_id)
    user=users_collection.find_one({"client_id":data.client_id,"mobile":data.mobile,"password":data.password})
    if not user:
        raise HTTPException(status_code=401,detail="Invalid mobile or password")
    if user.get("status")!="active":
        raise HTTPException(status_code=403,detail="User account inactive")
    users_collection.update_one({"_id":user["_id"]},{"$set":{"last_login":datetime.utcnow()}})
    return {"message":"Login successful","user":serialize_user(user)}

@router.post("/demo-login")
def demo_login(client_id:str=Query(...)):
    check_client(client_id)
    user=users_collection.find_one({"client_id":client_id,"is_demo":True})
    if not user:
        demo={
            "client_id":client_id,
            "full_name":"Demo User",
            "username":"DEMO123",
            "mobile":"DEMO123",
            "password":"demo123",
            "role":"demo",
            "balance":0,
            "status":"active",
            "is_demo":True,
            "created_at":datetime.utcnow(),
            "updated_at":datetime.utcnow()
        }
        result=users_collection.insert_one(demo)
        user=users_collection.find_one({"_id":result.inserted_id})
    return {"message":"Demo login successful","user":serialize_user(user)}

@router.post("/forgot-password")
def forgot_password(data:ForgotPassword):
    check_client(data.client_id)
    user=users_collection.find_one({"client_id":data.client_id,"mobile":data.mobile})
    if not user:
        raise HTTPException(status_code=404,detail="Mobile number not registered")
    reset_request={
        "client_id":data.client_id,
        "user_id":str(user["_id"]),
        "name":data.name,
        "mobile":data.mobile,
        "status":"pending",
        "created_at":datetime.utcnow()
    }
    password_reset_collection.insert_one(reset_request)
    return {"message":"Password reset request submitted"}

@router.get("/users")
def get_users(client_id:str=Query(...)):
    check_client(client_id)
    users=list(users_collection.find({"client_id":client_id}).sort("created_at",-1))
    return {"users":[serialize_user(user) for user in users]}

@router.get("/users/{user_id}")
def get_user(user_id:str,client_id:str=Query(...)):
    check_client(client_id)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400,detail="Invalid user id")
    user=users_collection.find_one({"_id":ObjectId(user_id),"client_id":client_id})
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return {"user":serialize_user(user)}

@router.put("/users/{user_id}")
def update_user(user_id:str,data:UserUpdate,client_id:str=Query(...)):
    check_client(client_id)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400,detail="Invalid user id")
    update_data={k:v for k,v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400,detail="No data to update")
    update_data["updated_at"]=datetime.utcnow()
    result=users_collection.update_one({"_id":ObjectId(user_id),"client_id":client_id},{"$set":update_data})
    if result.matched_count==0:
        raise HTTPException(status_code=404,detail="User not found")
    user=users_collection.find_one({"_id":ObjectId(user_id),"client_id":client_id})
    return {"message":"User updated successfully","user":serialize_user(user)}