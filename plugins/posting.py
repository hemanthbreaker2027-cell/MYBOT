import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.states import States
from helpers.decorators import admin_only
from pyrogram.enums import ChatType
from database.mongo import get_stickers

@Client.on_message(filters.command(["channels", "groups"]) & filters.private)
@admin_only
async def list_chats(client, message):
    if not userbot: return await message.reply_text("❌ UserBot not configured.")

    cmd = message.command[0]
    await message.reply_text(f"🔍 **Fetching your {cmd}...**")

    buttons = []
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat
        if cmd == "channels" and chat.type == ChatType.CHANNEL:
            buttons.append([InlineKeyboardButton(chat.title, callback_data=f"sel_post_{chat.id}")])
        elif cmd == "groups" and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            buttons.append([InlineKeyboardButton(chat.title, callback_data=f"sel_post_{chat.id}")])

    if not buttons:
        return await message.reply_text(f"No {cmd} found.")

    await message.reply_text(f"📋 **Select a {cmd[:-1]} to post:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_callback_query(filters.regex(r"^sel_post_"))
async def select_for_post(client, query):
    chat_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    await States.set_state(user_id, "COLLECT_POSTS", {"chat_id": chat_id, "messages": []})
    await query.edit_message_text(f"📝 **Selected Chat ID:** `{chat_id}`\n\nSend your posts now. Use `/done` when finished.")

@Client.on_message(filters.command("done") & filters.private)
@admin_only
async def done_command(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if state == "COLLECT_POSTS":
        chat_id = data["chat_id"]
        messages = data["messages"] # List of {"chat_id": int, "message_id": int}
        if not messages:
            return await message.reply_text("No posts collected.")

        status = await message.reply_text(f"🚀 **Posting {len(messages)} messages...**")
        stickers = await get_stickers()

        for msg_ref in messages:
            try:
                # Use UserBot instance (userbot) instead of Bot instance (client)
                await userbot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=msg_ref["chat_id"],
                    message_id=msg_ref["message_id"]
                )

                if stickers:
                    await userbot.send_sticker(chat_id, random.choice(stickers))

                await asyncio.sleep(0.5) # Anti-flood
            except Exception as e:
                await message.reply_text(f"❌ **Error posting:** {e}")

        await status.edit_text("✅ **Posting finished!**")
        await States.clear_state(user_id)

    elif state == "COLLECT_STICKERS":
        stickers = data.get("stickers", [])
        await message.reply_text(f"✅ **Collected {len(stickers)} stickers.**")
        await States.clear_state(user_id)

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done"]))
async def collect_messages(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    if state == "COLLECT_POSTS":
        msg_ref = {"chat_id": message.chat.id, "message_id": message.id}
        current_msgs = state_data["data"].get("messages", [])
        current_msgs.append(msg_ref)
        await States.update_data(user_id, messages=current_msgs)
    elif state == "COLLECT_STICKERS":
        if message.sticker:
            from database.mongo import add_sticker
            await add_sticker(message.sticker.file_id)
            current_stickers = state_data["data"].get("stickers", [])
            current_stickers.append(message.sticker.file_id)
            await States.update_data(user_id, stickers=current_stickers)
            await message.reply_text("✅ Sticker saved.")
