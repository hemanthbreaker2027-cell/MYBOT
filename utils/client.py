import os
from pyrogram import Client
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING_SESSION = os.getenv("STRING_SESSION")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Defaults if not provided in env for the main bot
API_ID = int(API_ID) if API_ID else 2040
API_HASH = API_HASH if API_HASH else "b18441a1ff607e106bee3edad22c6834"

bot = Client(
    "manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="modules")
)

userbot = None
if STRING_SESSION:
    userbot = Client(
        "userbot_client",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        plugins=dict(root="modules")
    )
