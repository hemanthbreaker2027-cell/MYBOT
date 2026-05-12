from pyrogram import Client, filters
from utils.client import OWNER_ID
from database.mongo import add_admin, remove_admin, get_admins
from utils.decorators import admin_only

@Client.on_message(filters.command("add_admin") & filters.private)
@admin_only
async def add_admin_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/add_admin USER_ID`")

    try:
        user_id = int(message.command[1])
        await add_admin(user_id)
        await message.reply_text(f"✅ **User `{user_id}` has been promoted to Admin.**")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID.** Please provide a numeric ID.")

@Client.on_message(filters.command("remove_admin") & filters.private)
@admin_only
async def remove_admin_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/remove_admin USER_ID`")

    try:
        user_id = int(message.command[1])
        if user_id == OWNER_ID:
            return await message.reply_text("❌ **Cannot demote the Owner.**")

        await remove_admin(user_id)
        await message.reply_text(f"🗑 **User `{user_id}` has been removed from Admins.**")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID.**")

@Client.on_message(filters.command("admins") & filters.private)
@admin_only
async def list_admins(client, message):
    admins = await get_admins()

    text = "👮 **Management Team:**\n\n"
    text += f"👑 **Owner:** `{OWNER_ID}`\n"

    if admins:
        text += "\n🛡 **Administrators:**\n"
        for admin in admins:
            if admin != OWNER_ID:
                text += f"• `{admin}`\n"

    await message.reply_text(text)
