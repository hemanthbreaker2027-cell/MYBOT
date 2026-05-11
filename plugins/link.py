from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.decorators import admin_only
from pyrogram.enums import ChatType, ChatMemberStatus

@Client.on_message(filters.command("link") & filters.private)
@admin_only
async def link_cmd(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ UserBot not configured or not running.")
    buttons = [
        [
            InlineKeyboardButton("📢 Channels", callback_data="lnk_list_channels"),
            InlineKeyboardButton("👥 Groups", callback_data="lnk_list_groups")
        ]
    ]
    await message.reply_text("🔗 **Get link for:**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^lnk_list_"))
async def lnk_list_chats(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    target = query.data.split("_")[2]
    buttons = []
    async for dialog in userbot.get_dialogs():
        chat = dialog.chat
        try:
            if target == "channels" and chat.type == ChatType.CHANNEL:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"lnk_get_{chat.id}")])
            elif target == "groups" and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await userbot.get_chat_member(chat.id, "me")
                if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    buttons.append([InlineKeyboardButton(chat.title, callback_data=f"lnk_get_{chat.id}")])
        except Exception:
            continue

    if not buttons:
        return await query.edit_message_text(f"No {target} found where you are admin.")

    await query.edit_message_text(f"📋 **Select a {target[:-1]}:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@Client.on_callback_query(filters.regex(r"^lnk_get_"))
async def lnk_get(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    chat_id = int(query.data.split("_")[2])
    chat = await userbot.get_chat(chat_id)

    if chat.username:
        await query.edit_message_text(f"🌍 **Public Link:** https://t.me/{chat.username}")
    else:
        buttons = [
            [
                InlineKeyboardButton("📩 Request Link", callback_data=f"lnk_req_{chat_id}"),
                InlineKeyboardButton("🔗 Normal Invite", callback_data=f"lnk_norm_{chat_id}")
            ]
        ]
        await query.edit_message_text(f"🔒 **Private Chat:** `{chat_id}`\nSelect link type:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^lnk_(req|norm)_"))
async def lnk_gen(client, query):
    if not userbot or not userbot.is_connected: return await query.answer("UserBot not running", show_alert=True)
    action, chat_id = query.data.split("_")[1], int(query.data.split("_")[2])
    try:
        if action == "req":
            link = await userbot.create_chat_invite_link(chat_id, creates_join_request=True)
        else:
            link = await userbot.create_chat_invite_link(chat_id)
        await query.edit_message_text(f"✅ **Link:** {link.invite_link}")
    except Exception as e:
        await query.edit_message_text(f"❌ **Error:** {e}")
