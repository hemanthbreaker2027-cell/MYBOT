# 🚀 Premium Telegram UserBot Manager

An advanced, production-ready Telegram UserBot management system built with Python 3.12+, Pyrogram, and Telethon. Featuring a clean architecture, MongoDB persistence, and a sleek, anime-inspired futuristic UI.

## ✨ Features

- 🛠 **Entity Management**: Create and delete channels, groups, and supergroups instantly.
- 📢 **Advanced Posting**: Broadcast messages (including media groups, polls, and formatted text) to multiple entities.
- 🎭 **Sticker Engine**: Automatically append random stickers from your custom collection to every post.
- 🛡 **Secure Admin System**: Multi-level admin access with persistent database storage.
- 🔑 **Session Generator**: Built-in, secure session string generator for Pyrogram and Telethon.
- 📦 **Docker Support**: Ready for production deployment with Docker and Docker Compose.
- ☁️ **Cloud Compatible**: Optimized for Railway, Render, Koyeb, and VPS.

---

## 🛠 Commands

### 👮 Admin Commands
- `/start` - Main control center and help menu.
- `/create` - Multi-step wizard to create new channels/groups.
- `/channels` - List and post to owned channels.
- `/groups` - List and post to owned groups.
- `/delete` - Safely delete owned entities with confirmation.
- `/link` - Manage and generate invite links.
- `/random_sticker` - Add stickers to the auto-posting engine.
- `/sticker_mode` - Toggle the automatic sticker injection AFTER each post.
- `/add_admin` - [Owner Only] Promote a user to admin.
- `/remove_admin` - [Owner Only] Demote an admin.

### 👤 User Commands
- `/gen_string` - Securely generate Pyrogram/Telethon session strings.

---

## 🚀 Deployment Guide

### 1. Environment Setup
Create a `.env` file in the root directory:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
STRING_SESSION=your_userbot_string_session
OWNER_ID=your_telegram_id
MONGO_URI=your_mongodb_uri
```

### 2. Local Deployment
```bash
pip install -r requirements.txt
python main.py
```

### 3. Docker Deployment
```bash
docker-compose up -d --build
```

### 4. Cloud Deployment (Railway / Render / Koyeb)
1. Fork this repository.
2. Connect your repository to the platform.
3. Set the Environment Variables.
4. The bot will automatically start the health check server on port `8080`.

---

## 🏗 Project Architecture

```text
/
├── bot/                # Core bot logic
├── database/           # MongoDB persistence layer
├── modules/            # Command handlers and features
├── utils/              # Helper functions and decorators
├── main.py             # Entry point
├── Dockerfile          # Production Docker image
└── docker-compose.yml  # Multi-container setup
```

---

## 🤝 Troubleshooting & FAQ

**Q: Why isn't the UserBot starting?**
A: Ensure you have provided a valid `STRING_SESSION` in your `.env` file.

**Q: How do I get my API_ID?**
A: Visit [my.telegram.org](https://my.telegram.org), log in, and go to "API development tools".

**Q: Is it safe to generate strings here?**
A: Yes. The bot uses in-memory sessions for generation and never logs OTPs or passwords.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Developed with ❤️ for the Telegram community.*
