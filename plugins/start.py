from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.decorators import is_admin

HELP_TEXT = """
✨ **Welcome to UserBot Manager!** ✨

I am your advanced control center for Telegram automation.

🛠 **Admin Commands:**
• `/create` - Create channels/groups
• `/channels` - Manage and post to channels
• `/groups` - Manage and post to groups
• `/delete` - Delete owned entities
• `/link` - Manage invite links
• `/random_sticker` - Manage auto-sticker engine
• `/add_admin` - Add new administrators

👤 **User Commands:**
• `/gen_string` - Generate session strings

🚀 **Select an action below:**
"""

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
            "👋 **Hello!** I can help you generate Telegram session strings safely.\n\nUse `/gen_string` to start.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Generate String", callback_data="gen_string_start")]
            ])
        )
