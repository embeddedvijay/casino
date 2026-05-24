import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from games.aviator.router import router as aviator_router
from games.aviator.router import aviator_socket
from games.aviator.manager import game_loop as aviator_game_loop


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
            }
        ],
    }


app.include_router(aviator_router)


@app.websocket("/ws/aviator")
async def websocket_aviator(websocket: WebSocket):
    await aviator_socket(websocket)


# Old compatibility routes, taaki current frontend bhi break na ho
@app.websocket("/ws/game")
async def websocket_old_aviator(websocket: WebSocket):
    await aviator_socket(websocket)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(aviator_game_loop())