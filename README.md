# 🚀 Advanced Telegram UserBot Manager

A powerful, production-ready Telegram UserBot management system built with Python, Pyrogram, and Telethon.

## ✨ Features

- **Modern UI:** Clean, aesthetic, and mobile-friendly.
- **Session Generator:** Securely generate session strings for Pyrogram and Telethon.
- **Entity Management:** Create and delete channels/groups with ease.
- **Advanced Posting Engine:**
  - Collect unlimited posts and send them sequentially.
  - Preserve all formatting, media, and buttons.
  - Auto-inject random stickers after each post.
- **Secure Admin System:** Only the owner and authorized admins can access management tools.
- **Production Ready:** Full Docker support, persistent MongoDB storage.

## 🛠 Commands

### Admin Commands
- `/start` - Main menu and overview.
- `/create` - Multi-step wizard to create channels or groups.
- `/channels` - List and post to owned channels.
- `/groups` - List and post to owned groups.
- `/delete` - Select and delete owned entities.
- `/link` - Manage invite links (private/public).
- `/random_sticker` - Collect stickers for auto-injection.
- `/add_admin <user_id>` - Add a new administrator (Owner only).
- `/admins` - List all administrators.

### User Commands
- `/start` - Welcome message.
- `/gen_string` - Interactive session string generator.

## 🚀 Deployment

### Prerequisites
- Python 3.11+
- MongoDB URI
- Telegram `API_ID` and `API_HASH`
- Bot Token

### Local Deployment
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file from `sample.env` and fill in the values.
4. Run: `python main.py`

### Docker Deployment
```bash
docker-compose up -d --build
```

## ⚙️ Environment Variables
- `BOT_TOKEN`: Your Telegram Bot Token.
- `OWNER_ID`: Your Telegram User ID.
- `STRING_SESSION`: Your UserBot session string.
- `MONGO_URI`: Your MongoDB connection string.
- `API_ID`: Your Telegram API ID.
- `API_HASH`: Your Telegram API Hash.

## 🔒 Security
- All sensitive inputs (OTP, Passwords) are automatically deleted.
- OTPs and Passwords are never logged or stored.

## 📜 License
MIT License.
