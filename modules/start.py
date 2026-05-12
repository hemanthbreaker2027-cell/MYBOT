from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import is_admin

HELP_TEXT = """
✨ **U S E R B O T  M A N A G E R** ✨
━━━━━━━━━━━━━━━━━━━
🛡 **Welcome to the premium control center.**

🛠 **Admin Hub:**
• `/create` — *New Channels/Groups*
• `/channels` — *Broadcast to Channels*
• `/groups` — *Broadcast to Groups*
• `/delete` — *Remove Entities*
• `/link` — *Link Management*
• `/random_sticker` — *Sticker Engine*
• `/sticker_mode` — *Toggle Auto-Stickers*
• `/add_admin` — *Promote User*
• `/remove_admin` — *Demote User*
• `/cancel` — *Cancel ongoing process*

👤 **User Services:**
• `/gen_string` — *Safe Session Generation*

🚀 **Choose an operation to begin:**
━━━━━━━━━━━━━━━━━━━
"""

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message):
    from utils.states import States
    user_id = message.from_user.id
    await States.clear_state(user_id)
    await message.reply_text("✅ **Current operation has been cancelled.**")

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if await is_admin(user_id):
        buttons = [
            [
                InlineKeyboardButton("📢 Channels", callback_data="manage_channels"),
                InlineKeyboardButton("👥 Groups", callback_data="manage_groups")
            ],
            [
                InlineKeyboardButton("🆕 Create", callback_data="create_entity"),
                InlineKeyboardButton("🗑 Delete", callback_data="delete_entity")
            ],
            [
                InlineKeyboardButton("🎭 Stickers", callback_data="manage_stickers"),
                InlineKeyboardButton("🔑 Gen String", callback_data="gen_string_start")
            ]
        ]
        await message.reply_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(
            "👋 **Greetings!**\n\nI am specialized in generating secure Telegram session strings for **Pyrogram** and **Telethon**.\n\n🛡 Use the button below to start.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Generate String", callback_data="gen_string_start")]
            ])
        )
