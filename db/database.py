import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = "reminders.db"


async def get_db() -> aiosqlite.Connection:
    return await aiosqlite.connect(DB_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                timezone TEXT NOT NULL DEFAULT 'UTC',
                is_sent INTEGER NOT NULL DEFAULT 0
            )
        """)
        await db.commit()
        logger.info("Database initialized")
        