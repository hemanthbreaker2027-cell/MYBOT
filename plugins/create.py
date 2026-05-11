import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.states import States
from helpers.decorators import admin_only

@Client.on_message(filters.command("create") & filters.private)
@admin_only
async def create_cmd(client, message):
    user_id = message.from_user.id
    if not userbot or not userbot.is_connected:
        return await message.reply_text("❌ UserBot is not running. Please check your `STRING_SESSION`.")

    buttons = [
        [
            InlineKeyboardButton("📢 Channel", callback_data="cr_type_channel"),
            InlineKeyboardButton("👥 Group", callback_data="cr_type_group")
        ]
    ]
    await message.reply_text("❓ **What do you want to create?**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^cr_"))
async def handle_create_callback(client, query):
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[1]

    if action == "type":
        chat_type = data[2]
        await States.set_state(user_id, "CREATE_NAME", {"chat_type": chat_type})
        await query.edit_message_text(f"🆕 **Send the name for the new {chat_type.capitalize()}:**")

    elif action == "privacy":
        privacy = data[2]
        await States.update_data(user_id, privacy=privacy)
        if privacy == "public":
            await States.set_state(user_id, "CREATE_USERNAME")
            await query.edit_message_text("🌍 **Send a public username (without @):**")
        else:
            await finalize_creation(client, query)

async def finalize_creation(client, query_or_msg, user_id=None):
    if user_id is None:
        user_id = query_or_msg.from_user.id

    state_data = await States.get_state(user_id)
    data = state_data["data"]

    name = data.get("name", "Unnamed")
    desc = data.get("description", "Created via UserBot Manager")
    privacy = data.get("privacy", "private")
    username = data.get("username")
    chat_type = data.get("chat_type", "channel")
    image = data.get("image")

    edit_func = query_or_msg.edit_message_text if hasattr(query_or_msg, "edit_message_text") else query_or_msg.edit_text
    await edit_func("⏳ **Creating...**")

    try:
        if chat_type == "channel":
            chat = await userbot.create_channel(str(name), str(desc))
        else:
            chat = await userbot.create_supergroup(str(name), str(desc))

        if image:
            await userbot.set_chat_photo(chat.id, photo=image)
            if os.path.exists(image): os.remove(image)

        invite_link = ""
        if privacy == "public" and username:
            try:
                await userbot.set_chat_username(chat.id, str(username))
                invite_link = f"https://t.me/{username}"
            except Exception as ue:
                invite_link = await userbot.export_chat_invite_link(chat.id)
                await query_or_msg.reply_text(f"⚠️ **Username Error:** {ue}\nCreated as Private instead.")
        else:
            invite_link = await userbot.export_chat_invite_link(chat.id)

        await edit_func(
            f"✅ **{chat_type.capitalize()} Created!**\n\n"
            f"**Name:** {name}\n"
            f"**ID:** `{chat.id}`\n"
            f"**Link:** {invite_link}"
        )
    except Exception as e:
        await edit_func(f"❌ **Failed to create:** {e}")

    await States.clear_state(user_id)
