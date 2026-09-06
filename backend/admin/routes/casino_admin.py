from datetime import datetime
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from database import db
router=APIRouter(prefix="/api/admin",tags=["Casino Admin"])

DEFAULT_GAMES=[
{"key":"AVIATOR","name":"Aviator","enabled":True,"min_bet":10,"max_bet":10000,"house_edge":1.0,"max_multiplier":100,"waiting_seconds":10,"result_seconds":5,"description":"Multiplier betting game"},
{"key":"DRAGON_TIGER","name":"Dragon Tiger","enabled":True,"min_bet":10,"max_bet":10000,"house_edge":1.0,"max_multiplier":8,"waiting_seconds":10,"result_seconds":5,"description":"Card comparison game"},
{"key":"LUCKY_RACE","name":"Lucky Race","enabled":True,"min_bet":10,"max_bet":10000,"house_edge":1.0,"max_multiplier":8,"waiting_seconds":10,"result_seconds":5,"description":"Racing betting game"},
{"key":"MATKA","name":"Matka","enabled":True,"min_bet":10,"max_bet":10000,"house_edge":1.0,"max_multiplier":90,"waiting_seconds":10,"result_seconds":5,"description":"Matka number game"}]

class CasinoSettingsBody(BaseModel):
 casino_name:str=Field(min_length=2,max_length=80)
 casino_short_name:str=Field(min_length=2,max_length=30)
 telegram_admin_id:str=""
 maintenance_mode:bool=False

class GamePatch(BaseModel):enabled:bool
class GameBody(BaseModel):
 key:str
 name:str
 enabled:bool=True
 min_bet:float=10
 max_bet:float=10000
 house_edge:float=1
 max_multiplier:float=100
 waiting_seconds:int=10
 result_seconds:int=5
 description:str=""

async def ensure_admin_defaults():
 if await db.casino_settings.count_documents({})==0:await db.casino_settings.insert_one({"casino_name":"GOLD365 CASINO","casino_short_name":"GOLD365","telegram_admin_id":"","maintenance_mode":False,"updated_at":datetime.utcnow()})
 for game in DEFAULT_GAMES:await db.game_settings.update_one({"key":game["key"]},{"$setOnInsert":game},upsert=True)

def clean(doc):
 if not doc:return None
 doc=dict(doc);doc.pop("_id",None)
 if isinstance(doc.get("updated_at"),datetime):doc["updated_at"]=doc["updated_at"].isoformat()
 return doc

@router.get("/casino-settings")
async def get_casino_settings():
 await ensure_admin_defaults();return clean(await db.casino_settings.find_one({}))

@router.put("/casino-settings")
async def save_casino_settings(body:CasinoSettingsBody):
 await db.casino_settings.update_one({}, {"$set":{**body.model_dump(),"updated_at":datetime.utcnow()}},upsert=True);return {"success":True}

@router.get("/games")
async def list_games():
 await ensure_admin_defaults();return [clean(x) async for x in db.game_settings.find({}).sort("name",1)]

@router.get("/games/{game_key}")
async def get_game(game_key:str):
 await ensure_admin_defaults();doc=await db.game_settings.find_one({"key":game_key.upper()})
 if not doc:raise HTTPException(404,"Game not found")
 return clean(doc)

@router.put("/games/{game_key}")
async def save_game(game_key:str,body:GameBody):
 data=body.model_dump();data["key"]=game_key.upper();data["updated_at"]=datetime.utcnow();await db.game_settings.update_one({"key":data["key"]},{"$set":data},upsert=True);return {"success":True}

@router.patch("/games/{game_key}")
async def toggle_game(game_key:str,body:GamePatch):
 result=await db.game_settings.update_one({"key":game_key.upper()},{"$set":{"enabled":body.enabled,"updated_at":datetime.utcnow()}})
 if result.matched_count==0:raise HTTPException(404,"Game not found")
 return {"success":True,"enabled":body.enabled}

@router.get("/management/summary")
async def management_summary():
 users=await db.users.count_documents({});dep=await db.deposit_requests.aggregate([{"$match":{"status":"Approved"}},{"$group":{"_id":None,"total":{"$sum":"$amount"}}}]).to_list(1);wd=await db.withdrawals.aggregate([{"$match":{"status":"Approved"}},{"$group":{"_id":None,"total":{"$sum":"$amount"}}}]).to_list(1)
 return {"users":users,"deposits":dep[0]["total"] if dep else 0,"withdrawals":wd[0]["total"] if wd else 0,"pending_deposits":await db.deposit_requests.count_documents({"status":"Pending"}),"pending_withdrawals":await db.withdrawals.count_documents({"status":"Pending"}),"active_games":await db.game_settings.count_documents({"enabled":True})}
