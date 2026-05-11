import asyncio
import logging
from helpers.client import bot, userbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Bot...")
    await bot.start()

    if userbot:
        logger.info("Starting UserBot...")
        await userbot.start()
    else:
        logger.warning("UserBot STRING_SESSION not provided, UserBot will not start.")

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
