import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot, bot
from helpers.states import States
from helpers.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus
from database.mongo import get_stickers

@Client.on_message(filters.command(["channels", "groups"]) & filters.private)
@admin_only
async def list_chats(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ UserBot not configured or not running.")

    cmd = message.command[0]
    await message.reply_text(f"🔍 **Fetching your {cmd}...**")

    buttons = []
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat

        try:
            if cmd == "channels" and chat.type == ChatType.CHANNEL:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"sel_post_{chat.id}")])

            elif cmd == "groups" and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"sel_post_{chat.id}")])
        except Exception:
            continue

    if not buttons:
        return await message.reply_text(f"No {cmd} found where you are admin.")

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
        if not userbot or not userbot.is_connected:
            return await message.reply_text("❌ UserBot not running.")

        chat_id = data["chat_id"]
        messages = data["messages"]
        if not messages:
            return await message.reply_text("No posts collected.")

        status = await message.reply_text(f"🚀 **Posting messages...**")
        stickers = await get_stickers()

        grouped = []
        last_group_id = None
        current_group = []

        for m in messages:
            if m.get("media_group_id"):
                if m["media_group_id"] == last_group_id:
                    current_group.append(m)
                else:
                    if current_group:
                        grouped.append(current_group)
                    current_group = [m]
                    last_group_id = m["media_group_id"]
            else:
                if current_group:
                    grouped.append(current_group)
                    current_group = []
                    last_group_id = None
                grouped.append(m)
        if current_group:
            grouped.append(current_group)

        for item in grouped:
            try:
                if isinstance(item, list):
                    await userbot.copy_media_group(
                        chat_id=chat_id,
                        from_chat_id=item[0]["from_chat_id"],
                        message_id=item[0]["message_id"]
                    )
                else:
                    # To preserve buttons, we fetch the message first
                    orig_msg = await userbot.get_messages(item["from_chat_id"], item["message_id"])
                    await orig_msg.copy(chat_id)

                if stickers:
                    await userbot.send_sticker(chat_id, random.choice(stickers))

                await asyncio.sleep(0.5)
            except Exception as e:
                await message.reply_text(f"❌ **Error posting:** {e}")

        await status.edit_text("✅ **Posting finished!**")
        await States.clear_state(user_id)

    elif state == "COLLECT_STICKERS":
        stickers_list = data.get("stickers", [])
        await message.reply_text(f"✅ **Collected {len(stickers_list)} stickers.**")
        await States.clear_state(user_id)
