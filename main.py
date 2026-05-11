import asyncio
import logging
import os
from aiohttp import web
from utils.client import bot, userbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check server started on port {port}")

async def main():
    logger.info("Starting Bot...")
    await bot.start()

    if userbot:
        logger.info("Starting UserBot...")
        await userbot.start()
    else:
        logger.warning("UserBot STRING_SESSION not provided, UserBot will not start.")

    # Start health check server for platforms like Render/Koyeb
    await start_web_server()

    logger.info("✅ System is running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        loop.run_until_complete(bot.stop())
        if userbot:
            loop.run_until_complete(userbot.stop())
