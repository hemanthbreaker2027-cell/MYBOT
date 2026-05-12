import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL) if MONGO_URL else None
db = client["userbot_manager"] if client else None

# Collections
admins_coll = db["admins"] if db is not None else None
stickers_coll = db["stickers"] if db is not None else None
settings_coll = db["settings"] if db is not None else None

async def add_admin(user_id: int):
    if admins_coll is not None:
        await admins_coll.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_admin(user_id: int):
    if admins_coll is not None:
        await admins_coll.delete_one({"user_id": user_id})

async def get_admins():
    if admins_coll is not None:
        cursor = admins_coll.find({})
        docs = await cursor.to_list(length=100)
        return [doc["user_id"] for doc in docs]
    return []

async def is_admin_db(user_id: int, owner_id: int):
    if user_id == owner_id:
        return True
    if admins_coll is not None:
        admin = await admins_coll.find_one({"user_id": user_id})
        return admin is not None
    return False

async def add_sticker(file_id: str):
    if stickers_coll is not None:
        await stickers_coll.update_one({"file_id": file_id}, {"$set": {"file_id": file_id}}, upsert=True)

async def get_stickers():
    if stickers_coll is not None:
        cursor = stickers_coll.find({})
        docs = await cursor.to_list(length=1000)
        return [doc["file_id"] for doc in docs]
    return []

async def set_setting(key: str, value):
    if settings_coll is not None:
        await settings_coll.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

async def get_setting(key: str, default=None):
    if settings_coll is not None:
        doc = await settings_coll.find_one({"key": key})
        return doc["value"] if doc else default
    return default
