from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import is_admin
from utils.states import States

HELP_TEXT = """
✨ **U S E R B O T  P R E M I U M** ✨
━━━━━━━━━━━━━━━━━━━
🚀 **High-Performance Content Manager**

🛠 **Core Management:**
• `/create` — *Deploy Channels/Groups*
• `/channels` — *Smart Broadcast (Channels)*
• `/groups` — *Smart Broadcast (Groups)*
• `/delete` — *Quick Removal*

🎨 **Engine Control:**
• `/random_sticker` — *Build Sticker Vault*
• `/sticker_mode` — *Auto-Sticker Toggle*
• `/cancel` — *Abort Current Flow*

👮 **Team Control:**
• `/admins` — *View Team*
• `/add_admin` — *Promote*
• `/remove_admin` — *Demote*

👤 **Tools:**
• `/gen_string` — *Session Generator*

━━━━━━━━━━━━━━━━━━━
✨ *Powered by Premium Architecture*
"""

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message):
    user_id = message.from_user.id
    await States.clear_state(user_id)
    await message.reply_text("✅ **All active processes have been terminated.**")

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if await is_admin(user_id):
        buttons = [
            [
                InlineKeyboardButton("📢 Channels", callback_data="list_channels"),
                InlineKeyboardButton("👥 Groups", callback_data="list_groups")
            ],
            [
                InlineKeyboardButton("🆕 Create", callback_data="start_create"),
                InlineKeyboardButton("🗑 Delete", callback_data="start_delete")
            ],
            [
                InlineKeyboardButton("🎭 Stickers", callback_data="manage_stickers"),
                InlineKeyboardButton("🔑 Gen String", callback_data="gen_string_start")
            ]
        ]
        await message.reply_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(
            "👋 **Welcome!**\n\nI am a specialized engine for generating secure **Pyrogram** and **Telethon** session strings.\n\n🛡 Click below to begin the secure generation process.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Generate Session", callback_data="gen_string_start")]
            ])
        )

@Client.on_callback_query(filters.regex(r"^manage_stickers$"))
async def manage_stickers_cb(client, query):
    from database.mongo import get_setting
    current = await get_setting("random_sticker_mode", False)
    status = "ON ✅" if current else "OFF ❌"

    buttons = [
        [InlineKeyboardButton(f"Mode: {status}", callback_data="toggle_sticker_mode")],
        [InlineKeyboardButton("➕ Add Stickers", callback_data="add_stickers_start")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]
    await query.edit_message_text("🎭 **Sticker Engine Settings**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^back_to_start$"))
async def back_to_start(client, query):
    user_id = query.from_user.id
    if await is_admin(user_id):
        buttons = [
            [
                InlineKeyboardButton("📢 Channels", callback_data="list_channels"),
                InlineKeyboardButton("👥 Groups", callback_data="list_groups")
            ],
            [
                InlineKeyboardButton("🆕 Create", callback_data="start_create"),
                InlineKeyboardButton("🗑 Delete", callback_data="start_delete")
            ],
            [
                InlineKeyboardButton("🎭 Stickers", callback_data="manage_stickers"),
                InlineKeyboardButton("🔑 Gen String", callback_data="gen_string_start")
            ]
        ]
        await query.edit_message_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^add_stickers_start$"))
async def add_stickers_cb(client, query):
    user_id = query.from_user.id
    await States.set_state(user_id, "COLLECT_STICKERS", {"stickers": []})
    await query.edit_message_text("🎨 **Send unlimited stickers now.**\n\nPress `/done` when you are finished.")

@Client.on_callback_query(filters.regex(r"^toggle_sticker_mode$"))
async def toggle_sticker_cb(client, query):
    from database.mongo import get_setting, set_setting
    current = await get_setting("random_sticker_mode", False)
    await set_setting("random_sticker_mode", not current)
    await manage_stickers_cb(client, query)

@Client.on_callback_query(filters.regex(r"^list_channels$"))
async def list_channels_cb(client, query):
    from modules.posting import list_chats_internal
    await list_chats_internal(client, query.message, "channels")

@Client.on_callback_query(filters.regex(r"^list_groups$"))
async def list_groups_cb(client, query):
    from modules.posting import list_chats_internal
    await list_chats_internal(client, query.message, "groups")

@Client.on_callback_query(filters.regex(r"^start_create$"))
async def start_create_cb(client, query):
    from modules.create import create_cmd_internal
    await create_cmd_internal(client, query.message)

@Client.on_callback_query(filters.regex(r"^start_delete$"))
async def start_delete_cb(client, query):
    # This assumes modules/delete.py has a similar internal function
    from modules.delete import delete_cmd_internal
    await delete_cmd_internal(client, query.message)
