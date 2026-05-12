import asyncio
import logging
from pyrogram import Client, filters
from utils.states import States
from utils.client import userbot, bot
from database.mongo import add_sticker

logger = logging.getLogger(__name__)

# Operational commands that should NOT be intercepted by the dispatcher
EXCLUDED_COMMANDS = [
    "start", "gen_string", "create", "channels", "groups",
    "delete", "link", "random_sticker", "add_admin", "done",
    "sticker_mode", "admins", "remove_admin", "cancel"
]

@Client.on_message(filters.private & ~filters.command(EXCLUDED_COMMANDS))
async def dispatcher(client, message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data.get("state")
    data = state_data.get("data", {})

    if not state:
        return

    # --- SESSION GENERATION FLOW ---
    if state.startswith("GS_"):
        from modules.gen_string import handle_gen_string_inputs
        await handle_gen_string_inputs(client, message)

    # --- CREATION FLOW ---
    elif state.startswith("CREATE_"):
        from modules.input_handler import handle_creation_inputs
        await handle_creation_inputs(client, message)

    # --- POST COLLECTION FLOW ---
    elif state == "COLLECT_POSTS":
        if not userbot or not userbot.is_connected:
            return await message.reply_text("❌ **UserBot not configured or not running.**")

        try:
            # We copy the message to the UserBot account's saved messages (or inbox)
            # to ensure the UserBot can "see" and "copy" it later.
            sent_msg = await message.copy(userbot.me.id)

            msg_ref = {
                "from_chat_id": userbot.me.id,
                "message_id": sent_msg.id,
                "media_group_id": message.media_group_id
            }

            current_msgs = data.get("messages", [])
            current_msgs.append(msg_ref)
            await States.update_data(user_id, messages=current_msgs)

            # Visual feedback
            if not message.media_group_id:
                await message.reply_text("📥 **Post collected.**", quote=True)
            else:
                # For albums, we use a reaction to avoid spamming
                try:
                    await message.react("📥")
                except:
                    pass

        except Exception as e:
            logger.error(f"Error in COLLECT_POSTS: {e}")
            await message.reply_text(f"❌ **Error collecting post:** `{e}`")

    # --- STICKER COLLECTION FLOW ---
    elif state == "COLLECT_STICKERS":
        if message.sticker:
            await add_sticker(message.sticker.file_id)
            # Also keep track in state for the current session if needed
            current_stickers = data.get("stickers", [])
            current_stickers.append(message.sticker.file_id)
            await States.update_data(user_id, stickers=current_stickers)
            await message.reply_text("✅ **Sticker saved.**", quote=True)
        else:
            await message.reply_text("⚠️ **Please send a sticker.**")
