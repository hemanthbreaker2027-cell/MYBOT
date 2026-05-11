import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import SessionPasswordNeeded, FloodWait
from telethon import TelegramClient
from telethon.sessions import StringSession
from helpers.states import States

@Client.on_message(filters.command("gen_string") & filters.private)
@Client.on_callback_query(filters.regex("gen_string_start"))
async def gen_string_start(client, message_or_query):
    is_callback = hasattr(message_or_query, "data")
    user_id = message_or_query.from_user.id

    buttons = [
        [
            InlineKeyboardButton("Pyrogram", callback_data="gs_pyrogram"),
            InlineKeyboardButton("Telethon", callback_data="gs_telethon")
        ],
        [
            InlineKeyboardButton("Pyrogram V2", callback_data="gs_pyrogram2"),
            InlineKeyboardButton("Telethon String", callback_data="gs_telethon_s")
        ]
    ]
    text = "🛡 **Select the library type for your session string:**"

    if is_callback:
        await message_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message_or_query.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^gs_"))
async def gs_ask_phone(client, query):
    lib_type = query.data.split("_")[1]
    user_id = query.from_user.id
    States.set_state(user_id, "GS_PHONE", {"type": lib_type})

    await query.edit_message_text("📱 **Send your phone number in international format.**\nExample: `+1234567890`",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]))

@Client.on_message(filters.private & ~filters.command(["start", "gen_string", "create", "channels", "groups", "delete", "link", "random_sticker", "add_admin", "done"]))
async def handle_input(client, message):
    user_id = message.from_user.id
    state_data = States.get_state(user_id)
    state = state_data["state"]
    data = state_data["data"]

    if not state:
        return

    if state == "GS_PHONE":
        phone = message.text.strip()
        States.update_data(user_id, phone=phone)
        States.set_state(user_id, "GS_OTP")

        api_id = int(os.getenv("API_ID", 2040))
        api_hash = os.getenv("API_HASH", "b18441a1ff607e106bee3edad22c6834")

        try:
            if "pyrogram" in data["type"]:
                temp_client = Client("temp", api_id=api_id, api_hash=api_hash, in_memory=True)
                await temp_client.connect()
                code_info = await temp_client.send_code(phone)
                States.update_data(user_id, client=temp_client, phone_code_hash=code_info.phone_code_hash)
            else:
                temp_client = TelegramClient(StringSession(), api_id, api_hash)
                await temp_client.connect()
                send_code = await temp_client.send_code_request(phone)
                States.update_data(user_id, client=temp_client, phone_code_hash=send_code.phone_code_hash)

            await message.reply_text("📩 **OTP Sent!**\nSend the OTP in space-separated format (e.g., `1 2 3 4 5`).")
        except Exception as e:
            await message.reply_text(f"❌ **Error:** {e}")
            States.clear_state(user_id)

    elif state == "GS_OTP":
        otp = message.text.replace(" ", "").strip()
        await message.delete() # Security: delete OTP

        lib_type = data["type"]
        temp_client = data["client"]
        phone = data["phone"]
        phone_code_hash = data["phone_code_hash"]

        try:
            if "pyrogram" in lib_type:
                try:
                    await temp_client.sign_in(phone, phone_code_hash, otp)
                except SessionPasswordNeeded:
                    States.set_state(user_id, "GS_PASSWORD")
                    await message.reply_text("🔐 **2FA Enabled!** Send your password:")
                    return

                string_session = await temp_client.export_session_string()
                await client.send_message(user_id, f"✅ **Your Session String:**\n\n`{string_session}`")
                await temp_client.disconnect()
            else:
                try:
                    await temp_client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
                except Exception as e:
                    if "password" in str(e).lower():
                        States.set_state(user_id, "GS_PASSWORD")
                        await message.reply_text("🔐 **2FA Enabled!** Send your password:")
                        return
                    raise e

                string_session = temp_client.session.save()
                await client.send_message(user_id, f"✅ **Your Session String:**\n\n`{string_session}`")
                await temp_client.disconnect()

            States.clear_state(user_id)
        except Exception as e:
            await client.send_message(user_id, f"❌ **Error:** {e}")
            States.clear_state(user_id)

    elif state == "GS_PASSWORD":
        password = message.text.strip()
        await message.delete() # Security: delete password

        lib_type = data["type"]
        temp_client = data["client"]

        try:
            if "pyrogram" in lib_type:
                await temp_client.check_password(password)
                string_session = await temp_client.export_session_string()
                await client.send_message(user_id, f"✅ **Your Session String:**\n\n`{string_session}`")
                await temp_client.disconnect()
            else:
                await temp_client.sign_in(password=password)
                string_session = temp_client.session.save()
                await client.send_message(user_id, f"✅ **Your Session String:**\n\n`{string_session}`")
                await temp_client.disconnect()

            States.clear_state(user_id)
        except Exception as e:
            await client.send_message(user_id, f"❌ **Error:** {e}")
            States.clear_state(user_id)

@Client.on_callback_query(filters.regex("cancel"))
async def cancel_action(client, query):
    user_id = query.from_user.id
    States.clear_state(user_id)
    await query.edit_message_text("❌ Action cancelled.")
