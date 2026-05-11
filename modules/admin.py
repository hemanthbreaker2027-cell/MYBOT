from pyrogram import Client, filters
from utils.client import OWNER_ID
from database.mongo import add_admin, remove_admin, get_admins

@Client.on_message(filters.command("add_admin") & filters.user(OWNER_ID))
async def add_admin_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/add_admin USER_ID`")

    try:
        user_id = int(message.command[1])
        await add_admin(user_id)
        await message.reply_text(f"✅ **User `{user_id}` has been promoted to Admin.**")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID.** Please provide a numeric ID.")

@Client.on_message(filters.command("remove_admin") & filters.user(OWNER_ID))
async def remove_admin_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/remove_admin USER_ID`")

    try:
        user_id = int(message.command[1])
        await remove_admin(user_id)
        await message.reply_text(f"🗑 **User `{user_id}` has been removed from Admins.**")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID.**")

@Client.on_message(filters.command("admins") & filters.user(OWNER_ID))
async def list_admins(client, message):
    admins = await get_admins()
    if not admins:
        return await message.reply_text("👮 **No additional administrators found.**")

    text = "👮 **Current Administrators:**\n\n"
    for admin in admins:
        text += f"• `{admin}`\n"
    await message.reply_text(text)
