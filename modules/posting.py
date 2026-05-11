import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.client import userbot, bot
from utils.states import States
from utils.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus
from database.mongo import get_stickers, get_setting, set_setting

@Client.on_message(filters.command(["channels", "groups"]) & filters.private)
@admin_only
async def list_chats(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ **UserBot not configured or not running.**")

    cmd = message.command[0]
    status_msg = await message.reply_text(f"🔍 **Scanning your {cmd}...**")

    buttons = []
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat

        try:
            if cmd == "channels" and chat.type == ChatType.CHANNEL:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    count = await userbot.get_chat_members_count(chat.id)
                    buttons.append([InlineKeyboardButton(f"{chat.title} ({count})", callback_data=f"sel_post_{chat.id}")])

            elif cmd == "groups" and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    count = await userbot.get_chat_members_count(chat.id)
                    buttons.append([InlineKeyboardButton(f"{chat.title} ({count})", callback_data=f"sel_post_{chat.id}")])
        except Exception:
            continue

    if not buttons:
        return await status_msg.edit_text(f"❌ **No {cmd} found where you have admin rights.**")

    await status_msg.edit_text(f"📋 **Select a {cmd[:-1]} to start posting:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_callback_query(filters.regex(r"^sel_post_"))
async def select_for_post(client, query):
    chat_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    await States.set_state(user_id, "COLLECT_POSTS", {"chat_id": chat_id, "messages": []})
    await query.edit_message_text(
        f"📝 **Chat Selected:** `{chat_id}`\n\n"
        "🚀 **Send the posts you want to queue.**\n"
        "✅ You can send text, media, albums, etc.\n"
        "🏁 Type `/done` when you are finished."
    )

@Client.on_message(filters.command("done") & filters.private)
@admin_only
async def done_command(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if state == "COLLECT_POSTS":
        if not userbot or not userbot.is_connected:
            return await message.reply_text("❌ **UserBot disconnected.**")

        chat_id = data["chat_id"]
        messages = data["messages"]
        if not messages:
            return await message.reply_text("⚠️ **No posts collected.**")

        status = await message.reply_text(f"🚀 **Dispatching items...**")
        stickers = await get_stickers()
        sticker_mode = await get_setting("random_sticker_mode", False)

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
                    # Fixed media group logic: need all message IDs
                    msg_ids = [x["message_id"] for x in item]
                    await userbot.copy_media_group(
                        chat_id=chat_id,
                        from_chat_id=item[0]["from_chat_id"],
                        message_id=msg_ids[0] # Pyrogram uses first ID to identify group
                    )
                else:
                    orig_msg = await userbot.get_messages(item["from_chat_id"], item["message_id"])
                    await orig_msg.copy(chat_id)

                # Send sticker AFTER every post/group if enabled
                if sticker_mode and stickers:
                    await userbot.send_sticker(chat_id, random.choice(stickers))

                await asyncio.sleep(1)
            except Exception as e:
                await message.reply_text(f"❌ **Error during posting:** `{e}`")

        await status.edit_text("✅ **All posts have been successfully delivered!**")
        await States.clear_state(user_id)

    elif state == "COLLECT_STICKERS":
        await message.reply_text("✅ **Sticker collection finished.**")
        await States.clear_state(user_id)

@Client.on_message(filters.command("sticker_mode") & filters.private)
@admin_only
async def toggle_sticker_mode(client, message):
    current = await get_setting("random_sticker_mode", False)
    new_val = not current
    await set_setting("random_sticker_mode", new_val)
    status = "ENABLED" if new_val else "DISABLED"
    await message.reply_text(f"🎭 **Random Sticker Mode is now {status}!**")
