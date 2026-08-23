import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from games.aviator.router import router as aviator_router
from games.aviator.router import aviator_socket
from games.aviator.manager import game_loop as aviator_game_loop

from games.dragon_tiger.router import router as dragon_tiger_router
from games.dragon_tiger.router import dragon_tiger_socket
from games.dragon_tiger.manager import game_loop as dragon_tiger_game_loop

from games.car_roulet.router import router as lucky_race_router
from games.car_roulet.router import lucky_race_socket
from games.car_roulet.manager import game_loop as lucky_race_game_loop

from games.matka.router import router as matka_router
from games.matka.router import matka_socket
from games.matka.manager import game_loop as matka_game_loop
from games.plinko.router import router as plinko_router
from games.chicken_road.router import router as chicken_road_router

from routes.auth_users import router as auth_users_router
from routes.users import router as users_router
from routes.casino_setup import router as casino_setup_router
from routes.portal import router as portal_router

from services.client_config import ensure_default_client, start_game_tasks
from database import db

from admin.routes.router import router as casino_admin_router

telegram_app = None



app = FastAPI(title="Casino Multi Game Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(aviator_router)
app.include_router(dragon_tiger_router)
app.include_router(lucky_race_router)
app.include_router(matka_router)
app.include_router(plinko_router)
app.include_router(chicken_road_router)
app.include_router(users_router)
app.include_router(auth_users_router)
app.include_router(casino_setup_router)
app.include_router(portal_router)
app.include_router(casino_admin_router)


@app.get("/")
def home():
    return {
        "message": "Casino server running",
        "games": [
            {"name": "Aviator", "api": "/api/games/aviator/state", "ws": "/ws/aviator", "page": "/aviator"},
            {"name": "Dragon Tiger", "api": "/api/games/dragon-tiger/state", "ws": "/ws/dragon-tiger", "page": "/dragon-tiger"},
            {"name": "Lucky Race", "api": "/api/games/lucky-race/state", "ws": "/ws/lucky-race", "page": "/lucky-race"},
        ],
        "portal_api": "/api/portal",
    }


@app.websocket("/ws/aviator")
async def websocket_aviator(websocket: WebSocket):
    await aviator_socket(websocket)


@app.websocket("/ws/game")
async def websocket_old_aviator(websocket: WebSocket):
    await aviator_socket(websocket)


@app.websocket("/ws/dragon-tiger")
async def websocket_dragon_tiger(websocket: WebSocket):
    await dragon_tiger_socket(websocket)


@app.websocket("/ws/lucky-race")
async def websocket_lucky_race(websocket: WebSocket):
    await lucky_race_socket(websocket)


@app.websocket("/ws/matka")
async def websocket_matka(websocket: WebSocket):
    await matka_socket(websocket)


@app.on_event("startup")
async def startup_event():
    await ensure_default_client(db)
    await start_game_tasks(
        db,
        aviator_game_loop,
        dragon_tiger_game_loop,
        lucky_race_game_loop,
        matka_game_loop,
    )
    print("✅ Server Ready")
