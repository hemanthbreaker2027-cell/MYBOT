from pyrogram import filters
from helpers.client import OWNER_ID
from database.mongo import is_admin_db

def admin_only(func):
    async def wrapper(client, message):
        user_id = message.from_user.id
        if await is_admin_db(user_id, OWNER_ID):
            return await func(client, message)
        # Optional: return a message for non-admins
    return wrapper

async def is_admin(user_id: int):
    return await is_admin_db(user_id, OWNER_ID)
