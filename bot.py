import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from configuration import settings


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'[%(asctime)s] - %(message)s',
        handlers=[
            logging.FileHandler('logs.log', mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ])
    settings.logger.info("Starting bot")
    bot = Bot(settings.bot_token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.middleware.setup(LoggingMiddleware())
    settings.register_handlers(dp)
    await settings.set_default_commands(dp)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
