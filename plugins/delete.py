from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus

@Client.on_message(filters.command("delete") & filters.private)
@admin_only
async def delete_cmd(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ UserBot not configured or not running.")
    buttons = [
        [
            InlineKeyboardButton("📢 Channels", callback_data="del_list_channels"),
            InlineKeyboardButton("👥 Groups", callback_data="del_list_groups")
        ]
    ]
    await message.reply_text("🗑 **What do you want to delete?**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^del_list_"))
async def del_list_chats(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    target = query.data.split("_")[2]
    buttons = []
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat
        try:
            if target == "channels" and chat.type == ChatType.CHANNEL:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status == ChatMemberStatus.OWNER:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"del_conf_{chat.id}")])
            elif target == "groups" and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status == ChatMemberStatus.OWNER:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"del_conf_{chat.id}")])
        except Exception:
            continue

    if not buttons:
        return await query.edit_message_text(f"No {target} found where you are owner.")

    await query.edit_message_text(f"📋 **Select a {target[:-1]} to DELETE:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_callback_query(filters.regex(r"^del_conf_"))
async def del_confirm(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    chat_id = int(query.data.split("_")[2])
    buttons = [
        [
            InlineKeyboardButton("🔥 DELETE", callback_data=f"del_do_{chat_id}"),
            InlineKeyboardButton("❌ CANCEL", callback_data="cancel")
        ]
    ]
    await query.edit_message_text(f"⚠️ **Confirm Deletion of ID:** `{chat_id}`?\nThis is irreversible!", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^del_do_"))
async def del_do(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    chat_id = int(query.data.split("_")[2])
    try:
        await userbot.delete_channel(chat_id)
        await query.edit_message_text(f"✅ **Chat `{chat_id}` deleted.**")
    except Exception as e:
        await query.edit_message_text(f"❌ **Error:** {e}")
