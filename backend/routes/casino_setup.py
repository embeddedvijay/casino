from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import db

router=APIRouter()

casino_clients=db["casino_clients"]
casino_settings=db["casino_settings"]

class CasinoSetup(BaseModel):
    client_id:str
    casino_name:str
    upi_id:str
    whatsapp_number:str=""
    telegram_link:str=""
    support_email:str=""

@router.post("/casino-setup")
async def save_casino_setup(data:CasinoSetup):
    client=await casino_clients.find_one({"client_id":data.client_id,"status":"active"})
    if not client:
        raise HTTPException(status_code=404,detail="Client not found or inactive")
    setup_data={
        "client_id":data.client_id,
        "casino_name":data.casino_name,
        "upi_id":data.upi_id,
        "whatsapp_number":data.whatsapp_number,
        "telegram_link":data.telegram_link,
        "support_email":data.support_email,
        "setup_completed":True,
        "updated_at":datetime.utcnow()
    }
    await casino_settings.update_one(
        {"client_id":data.client_id},
        {"$set":setup_data,"$setOnInsert":{"created_at":datetime.utcnow()}},
        upsert=True
    )
    await casino_clients.update_one(
        {"client_id":data.client_id},
        {"$set":{"setup_completed":True,"updated_at":datetime.utcnow()}}
    )
    return {"success":True,"message":"Casino setup saved successfully"}

@router.get("/casino-setup/{client_id}")
async def get_casino_setup(client_id:str):
    setting=await casino_settings.find_one({"client_id":client_id},{"_id":0})
    if not setting:
        return {"setup_completed":False}
    return setting