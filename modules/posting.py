import asyncio
import random
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.client import userbot, bot
from utils.states import States
from utils.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, RPCError
from database.mongo import get_stickers, get_setting

logger = logging.getLogger(__name__)

async def list_chats_internal(client, message, cmd):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ **UserBot is not connected.**")

    status_msg = await message.reply_text(f"🔍 **Scanning Authorized {cmd.capitalize()}...**")

    buttons = []
    try:
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
    except Exception as e:
        logger.error(f"Error listing chats: {e}")
        return await status_msg.edit_text(f"❌ **Error during scan:** `{e}`")

    if not buttons:
        return await status_msg.edit_text(f"❌ **No manageable {cmd} found.**")

    # Pagination could be added, for now showing top 20
    await status_msg.edit_text(f"📋 **Select target {cmd[:-1]}:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_message(filters.command(["channels", "groups"]) & filters.private)
@admin_only
async def list_chats(client, message):
    cmd = message.command[0]
    await list_chats_internal(client, message, cmd)

@Client.on_callback_query(filters.regex(r"^sel_post_"))
async def select_for_post(client, query):
    chat_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    await States.set_state(user_id, "COLLECT_POSTS", {"chat_id": chat_id, "messages": []})
    await query.edit_message_text(
        f"🎯 **Target Set:** `{chat_id}`\n\n"
        "📥 **Send your posts now (Text, Media, Albums).**\n"
        "🏁 Type `/done` when finished."
    )

@Client.on_message(filters.command("done") & filters.private)
@admin_only
async def done_command(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data.get("state")
    data = state_data.get("data", {})

    if state == "COLLECT_POSTS":
        target_chat_id = data.get("chat_id")
        messages = data.get("messages", [])

        if not messages:
            return await message.reply_text("⚠️ **Queue is empty.**")

        status = await message.reply_text("🚀 **Initiating sequential delivery...**")
        stickers = await get_stickers()
        sticker_mode = await get_setting("random_sticker_mode", False)

        # Process messages (grouping albums)
        processed_items = []
        last_group_id = None
        current_group = []

        for m in messages:
            gid = m.get("media_group_id")
            if gid:
                if gid == last_group_id:
                    current_group.append(m)
                else:
                    if current_group:
                        processed_items.append(current_group)
                    current_group = [m]
                    last_group_id = gid
            else:
                if current_group:
                    processed_items.append(current_group)
                    current_group = []
                    last_group_id = None
                processed_items.append(m)
        if current_group:
            processed_items.append(current_group)

        success_count = 0
        for item in processed_items:
            try:
                if isinstance(item, list):
                    # It's an album
                    msg_ids = [x["message_id"] for x in item]
                    await userbot.copy_media_group(
                        chat_id=target_chat_id,
                        from_chat_id=item[0]["from_chat_id"],
                        message_id=msg_ids[0]
                    )
                else:
                    # Single message
                    await userbot.copy_message(
                        chat_id=target_chat_id,
                        from_chat_id=item["from_chat_id"],
                        message_id=item["message_id"]
                    )

                success_count += 1
                if sticker_mode and stickers:
                    await userbot.send_sticker(target_chat_id, random.choice(stickers))

                await asyncio.sleep(1) # Interval between posts
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except Exception as e:
                logger.error(f"Posting error: {e}")
                await message.reply_text(f"❌ **Delivery Error:** `{e}`")

        await status.edit_text(f"✅ **Delivered {success_count} items to `{target_chat_id}`!**")
        await States.clear_state(user_id)

    elif state == "COLLECT_STICKERS":
        await message.reply_text("✅ **Sticker vault updated successfully.**")
        await States.clear_state(user_id)
