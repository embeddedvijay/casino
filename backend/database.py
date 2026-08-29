from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI=os.getenv("MONGO_URI","mongodb://localhost:27017")
DB_NAME=os.getenv("DB_NAME","Default")

client=MongoClient(MONGO_URI,serverSelectionTimeoutMS=5000,connectTimeoutMS=5000,appname="gold365-casino")
db=client[DB_NAME]

# GOLD365_ALL_GAMES_DEMO_POLICY_V1
from demo_database_proxy import wrap_database_for_demo
db = wrap_database_for_demo(db)
