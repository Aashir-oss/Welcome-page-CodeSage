from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "code_rag_db")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
def get_user_collection():
    return db["users"]
