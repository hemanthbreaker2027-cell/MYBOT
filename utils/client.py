import os
import logging
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mandatory variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING_SESSION = os.getenv("STRING_SESSION")
OWNER_ID_ENV = os.getenv("OWNER_ID")
MONGO_URL = os.getenv("MONGO_URL")

# Basic validation
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing! Bot will not start.")
if not OWNER_ID_ENV:
    logger.warning("OWNER_ID is missing! Some features may be restricted.")

try:
    OWNER_ID = int(OWNER_ID_ENV) if OWNER_ID_ENV else 0
except ValueError:
    logger.error("OWNER_ID must be an integer!")
    OWNER_ID = 0

# Defaults for API_ID/HASH (standard Pyrogram defaults or common values)
API_ID = int(API_ID) if API_ID else 2040
API_HASH = API_HASH if API_HASH else "b18441a1ff607e106bee3edad22c6834"

# Initialize Main Bot
bot = Client(
    "manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="modules"),
    workers=50
)

# Initialize UserBot (optional but recommended for full functionality)
userbot = None
if STRING_SESSION:
    userbot = Client(
        "userbot_client",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        plugins=dict(root="modules"),
        workers=50
    )
    logger.info("UserBot client initialized with plugins.")
else:
    logger.warning("STRING_SESSION not found. UserBot features will be unavailable.")
