import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.states import States
from helpers.decorators import admin_only
from plugins.create import ask_type, finalize_creation

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done"]))
async def handle_creation_inputs(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if not state or not state.startswith("CREATE_"):
        return

    # Creation Flow
    if state == "CREATE_NAME":
        await States.update_data(user_id, name=message.text)
        await States.set_state(user_id, "CREATE_IMAGE")
        await message.reply_text("🖼 **Send a photo for the avatar, or use /skip:**")

    elif state == "CREATE_IMAGE":
        if message.photo:
            file_path = await message.download()
            await States.update_data(user_id, image=file_path)
        elif message.text == "/skip":
            await States.update_data(user_id, image=None)
        else:
            return await message.reply_text("Please send a photo or /skip.")

        buttons = [
            [
                InlineKeyboardButton("🌍 Public", callback_data="cr_privacy_public"),
                InlineKeyboardButton("🔒 Private", callback_data="cr_privacy_private")
            ]
        ]
        await message.reply_text("🌍 **Public or Private?**", reply_markup=InlineKeyboardMarkup(buttons))

    elif state == "CREATE_USERNAME":
        await States.update_data(user_id, username=message.text.replace("@", ""))
        buttons = [
            [
                InlineKeyboardButton("📢 Channel", callback_data="cr_type_channel"),
                InlineKeyboardButton("👥 Group", callback_data="cr_type_group")
            ]
        ]
        await message.reply_text("❓ **What do you want to create?**", reply_markup=InlineKeyboardMarkup(buttons))
