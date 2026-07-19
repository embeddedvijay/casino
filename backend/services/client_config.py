import asyncio
from datetime import datetime
from admin.services.auth_service import new_password_record

game_tasks=[]

async def ensure_default_client(db):
    existing = db["clients"].find_one({"client_id": "demo"})

    update_data = {
        "$set": {
            "client_id": "demo",
            "client_name": "Demo Casino",
            "company_name": "Gold 365",
            "domain": "demo",
            "status": "active",
            "updated_at": datetime.utcnow()
        },
        "$setOnInsert": {
            "admin_username": "demo",
            "setup_completed": False,
            "must_change_password": True,
            "created_at": datetime.utcnow()
        }
    }

    if not existing:
        password_hash, password_salt = new_password_record("Demo@123")
        update_data["$setOnInsert"]["password_hash"] = password_hash
        update_data["$setOnInsert"]["password_salt"] = password_salt

    db["clients"].update_one(
        {"client_id": "demo"},
        update_data,
        upsert=True
    )

async def get_client_config(db,client_id="demo"):
    client=db["clients"].find_one({"client_id":client_id,"status":"active"},{"_id":0})
    print(client)
    if not client or not client.get("setup_completed"):
        return None

    settings=db["casino_settings"].find_one({"client_id":client_id},{"_id":0})
    markets=list(db["matka_markets"].find({"client_id":client_id,"status":"Active"},{"_id":0}))
    timings=list(db["matka_timings"].find({"client_id":client_id},{"_id":0}))
    star_lines=list(db["star_lines"].find({"client_id":client_id,"status":"Active"},{"_id":0}))

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
    game_tasks.append(asyncio.create_task(matka_game_loop()))

    print("Casino setup completed. Game loops started.")