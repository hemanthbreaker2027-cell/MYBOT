import os
import asyncio
from pyrogram import Client, filters
from helpers.states import States
from helpers.client import userbot, bot
from database.mongo import add_sticker

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done"]))
async def dispatcher(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if not state:
        return

    # --- SESSION GENERATION FLOW ---
    if state.startswith("GS_"):
        from plugins.gen_string import handle_gen_string_inputs
        await handle_gen_string_inputs(client, message)

    # --- CREATION FLOW ---
    elif state.startswith("CREATE_"):
        from plugins.input_handler import handle_creation_inputs
        await handle_creation_inputs(client, message)

    # --- POST COLLECTION FLOW ---
    elif state == "COLLECT_POSTS":
        if not userbot:
            return await message.reply_text("❌ UserBot not configured.")

        try:
            # Bot copies message to UserBot's Saved Messages so UserBot can access it later
            # userbot.me.id is the User's own ID
            sent_msg = await message.copy(userbot.me.id)

            msg_ref = {
                "from_chat_id": userbot.me.id,
                "message_id": sent_msg.id,
                "media_group_id": message.media_group_id
            }
            current_msgs = data.get("messages", [])
            current_msgs.append(msg_ref)
            await States.update_data(user_id, messages=current_msgs)
            await message.reply_text("📥 **Post collected.**", quote=True)
        except Exception as e:
            await message.reply_text(f"❌ **Error collecting post:** {e}")

    # --- STICKER COLLECTION FLOW ---
    elif state == "COLLECT_STICKERS":
        if message.sticker:
            await add_sticker(message.sticker.file_id)
            current_stickers = data.get("stickers", [])
            current_stickers.append(message.sticker.file_id)
            await States.update_data(user_id, stickers=current_stickers)
            await message.reply_text("✅ **Sticker saved.**", quote=True)
        else:
            await message.reply_text("⚠️ **Please send a sticker.**")
