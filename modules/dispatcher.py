import os
import asyncio
from pyrogram import Client, filters
from utils.states import States
from utils.client import userbot, bot
from database.mongo import add_sticker

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done", "sticker_mode", "admins", "remove_admin", "cancel"]))
async def dispatcher(client, message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

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
            # We relay the message to the UserBot account's chat with this Bot.
            # This ensures the UserBot has access to the content.
            # Note: message.copy() from Bot to UserBot lands in UserBot's inbox.
            sent_msg = await message.copy(userbot.me.id)

            msg_ref = {
                "from_chat_id": (await client.get_me()).id, # The Bot's ID is the chat where UserBot sees these messages
                "message_id": sent_msg.id,
                "media_group_id": message.media_group_id
            }
            current_msgs = data.get("messages", [])
            current_msgs.append(msg_ref)
            await States.update_data(user_id, messages=current_msgs)

            # Feedback for user
            if not message.media_group_id:
                await message.reply_text("📥 **Post collected.**", quote=True)
            # For media groups, we don't spam "collected" for every item
            else:
                # But we can show a small hint or react
                try:
                    await message.react("📥")
                except:
                    pass
        except Exception as e:
            await message.reply_text(f"❌ **Error collecting post:** `{e}`")

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
