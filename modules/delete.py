from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.client import userbot
from utils.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus

async def delete_cmd_internal(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ **UserBot is not running.**")

    buttons = [
        [
            InlineKeyboardButton("📢 Channels", callback_data="del_list_channels"),
            InlineKeyboardButton("👥 Groups", callback_data="del_list_groups")
        ]
    ]
    await message.reply_text("🗑 **Select entity type to delete:**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("delete") & filters.private)
@admin_only
async def delete_cmd(client, message):
    await delete_cmd_internal(client, message)

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
        return await query.edit_message_text(f"❌ **No {target} found where you are the owner.**")

    await query.edit_message_text(f"📋 **Select entity to DELETE:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_callback_query(filters.regex(r"^del_conf_"))
async def del_confirm(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    chat_id = int(query.data.split("_")[2])
    buttons = [
        [
            InlineKeyboardButton("🔥 DELETE", callback_data=f"del_do_{chat_id}"),
            InlineKeyboardButton("❌ CANCEL", callback_data="back_to_start")
        ]
    ]
    await query.edit_message_text(f"⚠️ **Confirm deletion of `{chat_id}`?**\nThis action is permanent!", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^del_do_"))
async def del_do(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    chat_id = int(query.data.split("_")[2])
    try:
        await userbot.delete_channel(chat_id)
        await query.edit_message_text(f"✅ **Entity `{chat_id}` has been purged.**")
    except Exception as e:
        await query.edit_message_text(f"❌ **Error:** `{e}`")
