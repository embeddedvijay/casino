import asyncio

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


app = FastAPI(title="Casino Multi Game Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Casino server running",
        "games": [
            {
                "name": "Aviator",
                "api": "/api/games/aviator/state",
                "ws": "/ws/aviator",
                "page": "/aviator",
            },
            {
                "name": "Dragon Tiger",
                "api": "/api/games/dragon-tiger/state",
                "ws": "/ws/dragon-tiger",
                "page": "/dragon-tiger",
            },
            {
                "name": "Lucky Race",
                "api": "/api/games/lucky-race/state",
                "ws": "/ws/lucky-race",
                "page": "/lucky-race",
            },
        ],
    }


app.include_router(aviator_router)
app.include_router(dragon_tiger_router)
app.include_router(lucky_race_router)


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


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(aviator_game_loop())
    asyncio.create_task(dragon_tiger_game_loop())
    asyncio.create_task(lucky_race_game_loop())