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
    States.set_state(user_id, "COLLECT_POSTS", {"chat_id": chat_id, "messages": []})
    await query.edit_message_text(f"📝 **Selected Chat ID:** `{chat_id}`\n\nSend your posts now. Use `/done` when finished.")

@Client.on_message(filters.command("done") & filters.private)
@admin_only
async def done_command(client, message):
    user_id = message.from_user.id
    state_data = States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if state == "COLLECT_POSTS":
        chat_id = data["chat_id"]
        messages = data["messages"]
        if not messages:
            return await message.reply_text("No posts collected.")

        status = await message.reply_text(f"🚀 **Posting {len(messages)} messages...**")
        stickers = await get_stickers()

        # Handle Media Groups
        processed_groups = set()

        for msg in messages:
            try:
                if msg.media_group_id:
                    if msg.media_group_id in processed_groups:
                        continue
                    # Copy the whole media group
                    await userbot.copy_media_group(chat_id, msg.chat.id, msg.id)
                    processed_groups.add(msg.media_group_id)
                else:
                    await msg.copy(chat_id)

                if stickers:
                    await userbot.send_sticker(chat_id, random.choice(stickers))

                await asyncio.sleep(0.5) # Anti-flood
            except Exception as e:
                await message.reply_text(f"❌ **Error posting:** {e}")

        await status.edit_text("✅ **Posting finished!**")
        States.clear_state(user_id)

    elif state == "COLLECT_STICKERS":
        stickers = data.get("stickers", [])
        await message.reply_text(f"✅ **Collected {len(stickers)} stickers.**")
        States.clear_state(user_id)

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done"]))
async def collect_messages(client, message):
    user_id = message.from_user.id
    state_data = States.get_state(user_id)
    if state_data["state"] == "COLLECT_POSTS":
        state_data["data"]["messages"].append(message)
    elif state_data["state"] == "COLLECT_STICKERS":
        if message.sticker:
            from database.mongo import add_sticker
            await add_sticker(message.sticker.file_id)
            state_data["data"]["stickers"].append(message.sticker.file_id)
            await message.reply_text("✅ Sticker saved.")
