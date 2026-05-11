import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.client import userbot
from utils.states import States
from utils.decorators import admin_only

@Client.on_message(filters.command("create") & filters.private)
@admin_only
async def create_cmd(client, message):
    user_id = message.from_user.id
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ **UserBot is not running.** Please check your `STRING_SESSION`.")

    buttons = [
        [
            InlineKeyboardButton("📢 Channel", callback_data="cr_type_channel"),
            InlineKeyboardButton("👥 Group", callback_data="cr_type_group")
        ]
    ]
    await message.reply_text("✨ **Step 1: What do you want to create?**", reply_markup=InlineKeyboardMarkup(buttons))

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
        await query.edit_message_text(f"🌐 **Step 2: Should the {chat_type} be Public or Private?**", reply_markup=InlineKeyboardMarkup(buttons))

    elif action == "privacy":
        privacy = data[2]
        await States.update_data(user_id, privacy=privacy)
        await States.set_state(user_id, "CREATE_NAME")
        await query.edit_message_text(f"📝 **Step 3: Send a Name for your {privacy} entity:**")

async def finalize_creation(client, query_or_msg, user_id=None):
    if user_id is None:
        user_id = query_or_msg.from_user.id

    state_data = await States.get_state(user_id)
    data = state_data["data"]

    name = data.get("name", "Unnamed")
    desc = data.get("description", "")
    privacy = data.get("privacy", "private")
    username = data.get("username")
    chat_type = data.get("chat_type", "channel")
    image = data.get("image")

    status_msg = await client.send_message(user_id, "⏳ **Creating your entity... Please wait.**")

    try:
        if chat_type == "channel":
            chat = await userbot.create_channel(str(name), str(desc))
        else:
            chat = await userbot.create_supergroup(str(name), str(desc))

        if image:
            try:
                await userbot.set_chat_photo(chat.id, photo=image)
                if os.path.exists(image): os.remove(image)
            except Exception as ie:
                await client.send_message(user_id, f"⚠️ **Warning:** Could not set profile photo: {ie}")

        invite_link = ""
        if privacy == "public" and username:
            try:
                await userbot.set_chat_username(chat.id, str(username))
                invite_link = f"https://t.me/{username}"
            except Exception as ue:
                invite_link = await userbot.export_chat_invite_link(chat.id)
                await client.send_message(user_id, f"⚠️ **Username Error:** {ue}\nEntity created as Private instead.")
        else:
            invite_link = await userbot.export_chat_invite_link(chat.id)

        res_text = (
            "✅ **Entity Created Successfully!**\n\n"
            f"👤 **Name:** `{name}`\n"
            f"🆔 **ID:** `{chat.id}`\n"
            f"🔗 **Link:** {invite_link}\n"
            f"🎭 **Type:** {chat_type.capitalize()}\n"
            f"🌐 **Privacy:** {privacy.capitalize()}"
        )
        await status_msg.edit_text(res_text)
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to create entity:** {e}")

    await States.clear_state(user_id)
