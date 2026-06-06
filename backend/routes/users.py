from fastapi import APIRouter,HTTPException,Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from database import db

router=APIRouter(prefix="/users",tags=["Users"])
users_collection=db["users"]
clients_collection=db["clients"]

class UserCreate(BaseModel):
    client_id:str
    username:str
    mobile:Optional[str]=None
    email:Optional[str]=None
    password:Optional[str]=None
    role:Optional[str]="user"
    balance:Optional[float]=0

class UserUpdate(BaseModel):
    username:Optional[str]=None
    mobile:Optional[str]=None
    email:Optional[str]=None
    password:Optional[str]=None
    role:Optional[str]=None
    balance:Optional[float]=None
    status:Optional[str]=None

def is_valid_object_id(value):
    return ObjectId.is_valid(value)

def check_client(client_id):
    client=clients_collection.find_one({"client_id":client_id})
    if not client:
        raise HTTPException(status_code=404,detail="Client not found")
    if client.get("status")!="active":
        raise HTTPException(status_code=403,detail="Client is not active")
    return client

def serialize_user(user):
    return {
        "id":str(user["_id"]),
        "client_id":user.get("client_id",""),
        "username":user.get("username",""),
        "mobile":user.get("mobile",""),
        "email":user.get("email",""),
        "role":user.get("role","user"),
        "balance":user.get("balance",0),
        "status":user.get("status","active"),
        "created_at":user.get("created_at"),
        "updated_at":user.get("updated_at")
    }

@router.post("/create")
def create_user(data:UserCreate):
    check_client(data.client_id)
    exists=users_collection.find_one({"client_id":data.client_id,"username":data.username})
    if exists:
        raise HTTPException(status_code=400,detail="Username already exists for this client")
    user=data.dict()
    user["status"]="active"
    user["created_at"]=datetime.utcnow()
    user["updated_at"]=datetime.utcnow()
    result=users_collection.insert_one(user)
    new_user=users_collection.find_one({"_id":result.inserted_id})
    return {"message":"User created successfully","user":serialize_user(new_user)}

@router.get("/")
def get_users(client_id:str=Query(...)):
    check_client(client_id)
    users=list(users_collection.find({"client_id":client_id}).sort("created_at",-1))
    return {"users":[serialize_user(user) for user in users]}

@router.get("/{user_id}")
def get_user(user_id:str,client_id:str=Query(...)):
    check_client(client_id)
    if not is_valid_object_id(user_id):
        raise HTTPException(status_code=400,detail="Invalid user id")
    user=users_collection.find_one({"_id":ObjectId(user_id),"client_id":client_id})
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return {"user":serialize_user(user)}

@router.put("/{user_id}")
def update_user(user_id:str,data:UserUpdate,client_id:str=Query(...)):
    check_client(client_id)
    if not is_valid_object_id(user_id):
        raise HTTPException(status_code=400,detail="Invalid user id")
    update_data={k:v for k,v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400,detail="No data to update")
    if "username" in update_data:
        exists=users_collection.find_one({"client_id":client_id,"username":update_data["username"],"_id":{"$ne":ObjectId(user_id)}})
        if exists:
            raise HTTPException(status_code=400,detail="Username already exists for this client")
    update_data["updated_at"]=datetime.utcnow()
    result=users_collection.update_one({"_id":ObjectId(user_id),"client_id":client_id},{"$set":update_data})
    if result.matched_count==0:
        raise HTTPException(status_code=404,detail="User not found")
    user=users_collection.find_one({"_id":ObjectId(user_id),"client_id":client_id})
    return {"message":"User updated successfully","user":serialize_user(user)}

@router.delete("/{user_id}")
def delete_user(user_id:str,client_id:str=Query(...)):
    check_client(client_id)
    if not is_valid_object_id(user_id):
        raise HTTPException(status_code=400,detail="Invalid user id")
    result=users_collection.delete_one({"_id":ObjectId(user_id),"client_id":client_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=404,detail="User not found")
    return {"message":"User deleted successfully"}