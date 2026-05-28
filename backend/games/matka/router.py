from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pymongo import MongoClient
from bson import ObjectId

from . import manager
from .schemas import MatkaBetRequest, MatkaClearRequest


router = APIRouter(
    prefix="/api/games/matka",
    tags=["Matka"],
)


MONGO_URL = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGO_URL)

market_db = mongo_client["local"]
market_collection = market_db["Market"]


def mongo_to_json(data):
    if isinstance(data, list):
        return [mongo_to_json(item) for item in data]

    if isinstance(data, dict):
        return {key: mongo_to_json(value) for key, value in data.items()}

    if isinstance(data, ObjectId):
        return str(data)

    return data


@router.get("/state")
def get_state():
    return manager.public_data()


@router.get("/results/latest")
def get_latest_matka_result():
    doc = market_collection.find_one(sort=[("_id", -1)])

    if not doc:
        return {
            "success": False,
            "message": "No result found",
            "Result": {},
        }

    return mongo_to_json(doc)


@router.get("/results/by-date/{date_key}")
def get_matka_result_by_date(date_key: str):
    doc = market_collection.find_one({"Date": date_key})

    if not doc:
        doc = market_collection.find_one({"_id": date_key})

    if not doc:
        return {
            "success": False,
            "message": "No result found",
            "Result": {},
        }

    return mongo_to_json(doc)


@router.post("/bet")
async def place_bet(req: MatkaBetRequest):
    return await manager.place_bet(req)


@router.post("/clear")
async def clear_bets(req: MatkaClearRequest):
    return await manager.clear_bets(req)


async def matka_socket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)