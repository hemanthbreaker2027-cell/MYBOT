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
    if not userbot:
        return await message.reply_text("❌ UserBot is not configured.")

    await States.set_state(user_id, "CREATE_NAME")
    await message.reply_text("🆕 **Send the name for the new Channel/Group:**")

@Client.on_callback_query(filters.regex(r"^cr_"))
async def handle_create_callback(client, query):
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[1]

    if action == "privacy":
        privacy = data[2]
        await States.update_data(user_id, privacy=privacy)
        if privacy == "public":
            await States.set_state(user_id, "CREATE_USERNAME")
            await query.edit_message_text("🌍 **Send a public username (without @):**")
        else:
            await ask_type(query)

    elif action == "type":
        chat_type = data[2]
        await States.update_data(user_id, chat_type=chat_type)
        await finalize_creation(client, query)

async def ask_type(query):
    buttons = [
        [
            InlineKeyboardButton("📢 Channel", callback_data="cr_type_channel"),
            InlineKeyboardButton("👥 Group", callback_data="cr_type_group")
        ]
    ]
    await query.edit_message_text("❓ **What do you want to create?**", reply_markup=InlineKeyboardMarkup(buttons))

async def finalize_creation(client, query):
    user_id = query.from_user.id
    state_data = await States.get_state(user_id)
    data = state_data["data"]

    name = data.get("name")
    privacy = data.get("privacy")
    username = data.get("username")
    chat_type = data.get("chat_type")
    image = data.get("image")

    await query.edit_message_text("⏳ **Creating...**")

    try:
        if chat_type == "channel":
            chat = await userbot.create_channel(name, "Created via UserBot Manager")
        else:
            chat = await userbot.create_supergroup(name, "Created via UserBot Manager")

        if image:
            await userbot.set_chat_photo(chat.id, photo=image)
            if os.path.exists(image): os.remove(image)

        invite_link = ""
        if privacy == "public":
            await userbot.set_chat_username(chat.id, username)
            invite_link = f"https://t.me/{username}"
        else:
            invite_link = await userbot.export_chat_invite_link(chat.id)

        await query.edit_message_text(
            f"✅ **{chat_type.capitalize()} Created!**\n\n"
            f"**Name:** {name}\n"
            f"**ID:** `{chat.id}`\n"
            f"**Link:** {invite_link}"
        )
    except Exception as e:
        await query.edit_message_text(f"❌ **Failed to create:** {e}")

    await States.clear_state(user_id)
