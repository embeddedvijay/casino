import asyncio
from datetime import datetime

game_tasks=[]

async def ensure_default_client(db):
    await db["clients"].update_one(
        {"client_id":"demo"},
        {"$set":{
            "client_id":"demo",
            "client_name":"Demo Casino",
            "company_name":"Gold 365",
            "domain":"demo",
            "status":"active",
            "updated_at":datetime.utcnow()
        },"$setOnInsert":{
            "setup_completed":False,
            "created_at":datetime.utcnow()
        }},
        upsert=True
    )

async def get_client_config(db,client_id="demo"):
    client=await db["clients"].find_one({"client_id":client_id,"status":"active"},{"_id":0})
    if not client or not client.get("setup_completed"):
        return None

    settings=await db["casino_settings"].find_one({"client_id":client_id},{"_id":0})
    markets=await db["matka_markets"].find({"client_id":client_id,"status":"Active"},{"_id":0}).to_list(None)
    timings=await db["matka_timings"].find({"client_id":client_id},{"_id":0}).to_list(None)
    star_lines=await db["star_lines"].find({"client_id":client_id,"status":"Active"},{"_id":0}).to_list(None)

    return {
        "client":client,
        "settings":settings,
        "markets":markets,
        "timings":timings,
        "star_lines":star_lines
    }

async def start_game_tasks(db,aviator_game_loop,dragon_tiger_game_loop,lucky_race_game_loop,matka_game_loop):
    config=await get_client_config(db,"demo")
    if not config:
        print("Casino setup not completed. Game loops not started.")
        return

    game_tasks.append(asyncio.create_task(aviator_game_loop()))
    game_tasks.append(asyncio.create_task(dragon_tiger_game_loop()))
    game_tasks.append(asyncio.create_task(lucky_race_game_loop()))
    game_tasks.append(asyncio.create_task(matka_game_loop(config)))

    print("Casino setup completed. Game loops started.")