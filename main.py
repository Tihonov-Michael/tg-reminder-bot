import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from db.database import init_db
from bot.handlers import start, reminders
from bot.middlewares.throttling import ThrottlingMiddleware
from scheduler.jobs import restore_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    scheduler = AsyncIOScheduler(timezone="UTC")

    # Middlewares
    dp.message.middleware(ThrottlingMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(reminders.router)

    # Init DB
    await init_db()

    # Restore scheduled jobs after restart
    await restore_jobs(bot, scheduler)

    scheduler.start()
    logger.info("Scheduler started")

    try:
        logger.info("Bot started")
        await dp.start_polling(bot, scheduler=scheduler)
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
    