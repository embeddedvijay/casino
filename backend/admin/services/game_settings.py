from database import db
async def get_game_setting(game_key:str):return await db.game_settings.find_one({"key":game_key.upper()}) or {}
async def is_game_enabled(game_key:str)->bool:
 doc=await get_game_setting(game_key);return bool(doc.get("enabled",True))
async def get_numeric_setting(game_key:str,field:str,default):
 doc=await get_game_setting(game_key)
 try:return type(default)(doc.get(field,default))
 except:return default


