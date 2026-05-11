import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.client import userbot
from helpers.states import States
from helpers.decorators import admin_only
from plugins.create import finalize_creation

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
        # For public, finalize immediately after getting username
        # But we need a query object for finalize_creation.
        # Let's refactor finalize_creation to take message or query.
        msg = await message.reply_text("⏳ **Finalizing creation...**")
        # We'll call a modified version or just re-implement here for simplicity.
        # Actually, let's keep it consistent.

        name = data.get("name")
        privacy = "public"
        username = message.text.replace("@", "")
        chat_type = data.get("chat_type")
        image = data.get("image")

        try:
            if chat_type == "channel":
                chat = await userbot.create_channel(name, "Created via UserBot Manager")
            else:
                chat = await userbot.create_supergroup(name, "Created via UserBot Manager")

            if image:
                await userbot.set_chat_photo(chat.id, photo=image)
                if os.path.exists(image): os.remove(image)

            await userbot.set_chat_username(chat.id, username)
            invite_link = f"https://t.me/{username}"

            await msg.edit_text(
                f"✅ **{chat_type.capitalize()} Created!**\n\n"
                f"**Name:** {name}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {invite_link}"
            )
        except Exception as e:
            await msg.edit_text(f"❌ **Failed to create:** {e}")

        await States.clear_state(user_id)
