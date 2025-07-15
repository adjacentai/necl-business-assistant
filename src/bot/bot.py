import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.config import TELEGRAM_BOT_TOKEN
from src.bot.routers import main_router
from src.bot import handlers

# Configure basic logging for the bot
logging.basicConfig(level=logging.INFO)

async def start_bot():
    """Initializes and starts the Telegram bot."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Include the router from handlers
    dp.include_router(main_router)

    logging.info("Starting bot...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}")
    finally:
        await bot.session.close()
        logging.info("Bot stopped.")

def main():
    """The main function to run the bot."""
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by admin.")

if __name__ == '__main__':
    main()
