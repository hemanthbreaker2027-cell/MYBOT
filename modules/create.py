import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired
from utils.client import userbot, bot
from utils.states import States
from utils.decorators import admin_only

logger = logging.getLogger(__name__)

async def create_cmd_internal(client, message):
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ **UserBot is not running.** Please check your `STRING_SESSION`.")

    buttons = [
        [
            InlineKeyboardButton("📢 Channel", callback_data="cr_type_channel"),
            InlineKeyboardButton("👥 Group", callback_data="cr_type_group")
        ]
    ]
    await message.reply_text("✨ **Step 1: Select Entity Type**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("create") & filters.private)
@admin_only
async def create_cmd(client, message):
    await create_cmd_internal(client, message)

@Client.on_callback_query(filters.regex(r"^cr_"))
async def handle_create_callback(client, query):
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[1]

    if action == "type":
        chat_type = data[2]
        await States.set_state(user_id, "CREATE_PRIVACY", {"chat_type": chat_type})
        buttons = [
            [
                InlineKeyboardButton("🌍 Public", callback_data="cr_privacy_public"),
                InlineKeyboardButton("🔒 Private", callback_data="cr_privacy_private")
            ]
        ]
        await query.edit_message_text(f"🌐 **Step 2: Set {chat_type.capitalize()} Privacy**", reply_markup=InlineKeyboardMarkup(buttons))

    elif action == "privacy":
        privacy = data[2]
        await States.update_data(user_id, privacy=privacy)
        await States.set_state(user_id, "CREATE_NAME")
        await query.edit_message_text(f"📝 **Step 3: Provide a Name for your {privacy} entity:**")

async def finalize_creation(client, query_or_msg, user_id=None):
    if user_id is None:
        user_id = query_or_msg.from_user.id

    state_data = await States.get_state(user_id)
    data = state_data.get("data", {})

    name = data.get("name", "Unnamed")
    desc = data.get("description", "")
    privacy = data.get("privacy", "private")
    username = data.get("username")
    chat_type = data.get("chat_type", "channel")
    image = data.get("image")

    status_msg = await client.send_message(user_id, "⏳ **Initializing deployment...**")

    try:
        if chat_type == "channel":
            chat = await userbot.create_channel(title=str(name), description=str(desc))
        else:
            chat = await userbot.create_supergroup(title=str(name), description=str(desc))

        # --- BOT PROMOTION ---
        # Note: In channels, you can promote a bot without it being a member.
        try:
            bot_me = await client.get_me()
            await userbot.promote_chat_member(
                chat.id,
                bot_me.id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_post_messages=True,
                    can_edit_messages=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_manage_video_chats=True,
                    is_anonymous=False
                )
            )
            promotion_status = "✅ **Bot promoted to Admin.**"
        except Exception as pe:
            logger.error(f"Promotion error: {pe}")
            promotion_status = f"⚠️ **Promotion failed:** `{pe}`"

        if image:
            try:
                await userbot.set_chat_photo(chat.id, photo=image)
                if os.path.exists(image): os.remove(image)
            except Exception as ie:
                await client.send_message(user_id, f"⚠️ **Photo Error:** `{ie}`")

        invite_link = ""
        if privacy == "public" and username:
            try:
                await userbot.set_chat_username(chat.id, str(username))
                invite_link = f"https://t.me/{username}"
            except Exception as ue:
                invite_link = await userbot.export_chat_invite_link(chat.id)
                await client.send_message(user_id, f"⚠️ **Username Occupied:** {ue}. Created as Private.")
        else:
            invite_link = await userbot.export_chat_invite_link(chat.id)

        res_text = (
            "✅ **Deployment Successful!**\n\n"
            f"👤 **Name:** `{name}`\n"
            f"🆔 **ID:** `{chat.id}`\n"
            f"🔗 **Link:** {invite_link}\n"
            f"🎭 **Type:** {chat_type.capitalize()}\n\n"
            f"{promotion_status}"
        )
        await status_msg.edit_text(res_text)
    except FloodWait as fw:
        await status_msg.edit_text(f"❌ **FloodWait:** Please wait {fw.value}s.")
    except Exception as e:
        logger.error(f"Creation error: {e}")
        await status_msg.edit_text(f"❌ **Deployment Failed:** `{e}`")

    await States.clear_state(user_id)
