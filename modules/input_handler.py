import os
from pyrogram import Client, filters
from utils.client import userbot
from utils.states import States
from utils.decorators import admin_only
from modules.create import finalize_creation

async def handle_creation_inputs(client, message):
    user_id = message.from_user.id
    state_data = await States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if state == "CREATE_NAME":
        if not message.text:
            return await message.reply_text("❌ **Please send a valid name.**")
        await States.update_data(user_id, name=message.text)
        await States.set_state(user_id, "CREATE_DESC")
        await message.reply_text("📝 **Step 4: Send a Description (optional), or /skip:**")

    elif state == "CREATE_DESC":
        desc = message.text if message.text != "/skip" else ""
        await States.update_data(user_id, description=desc)
        await States.set_state(user_id, "CREATE_IMAGE")
        await message.reply_text("🖼 **Step 5: Send a Photo for the avatar, or /skip:**")

    elif state == "CREATE_IMAGE":
        if message.photo:
            file_path = await message.download()
            await States.update_data(user_id, image=file_path)
        elif message.text == "/skip":
            await States.update_data(user_id, image=None)
        else:
            return await message.reply_text("⚠️ **Please send a photo or /skip.**")

        if data.get("privacy") == "public":
            await States.set_state(user_id, "CREATE_USERNAME")
            await message.reply_text("🌐 **Step 6: Send a Public Username (without @):**")
        else:
            await finalize_creation(client, message, user_id)

    elif state == "CREATE_USERNAME":
        if not message.text:
            return await message.reply_text("❌ **Please send a valid username.**")
        username = message.text.replace("@", "").strip()
        await States.update_data(user_id, username=username)
        await finalize_creation(client, message, user_id)
