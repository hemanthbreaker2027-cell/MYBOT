from pyrogram import Client, filters
from utils.states import States
from utils.decorators import admin_only

@Client.on_message(filters.command("random_sticker") & filters.private)
@admin_only
async def random_sticker_cmd(client, message):
    user_id = message.from_user.id
    await States.set_state(user_id, "COLLECT_STICKERS", {"stickers": []})
    await message.reply_text("🎨 **Send unlimited stickers.**\nUse `/done` when finished.")
