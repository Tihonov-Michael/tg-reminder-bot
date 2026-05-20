import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.queries import get_all_pending, mark_as_sent

logger = logging.getLogger(__name__)


async def send_reminder(bot: Bot, reminder_id: int, user_id: int, text: str):
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🔔 Напоминание:\n\n{text}",
        )
        await mark_as_sent(reminder_id)
        logger.info(f"Reminder {reminder_id} sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send reminder {reminder_id} to user {user_id}: {e}")


def schedule_reminder(
    bot: Bot,
    scheduler: AsyncIOScheduler,
    reminder_id: int,
    user_id: int,
    text: str,
    remind_at: datetime,
):
    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=remind_at,
        kwargs={
            "bot": bot,
            "reminder_id": reminder_id,
            "user_id": user_id,
            "text": text,
        },
        id=str(reminder_id),
        replace_existing=True,
    )
    logger.info(f"Scheduled reminder {reminder_id} for user {user_id} at {remind_at}")


async def restore_jobs(bot: Bot, scheduler: AsyncIOScheduler):
    reminders = await get_all_pending()
    now = datetime.utcnow()
    restored = 0
    skipped = 0

    for reminder in reminders:
        remind_at = datetime.fromisoformat(reminder["remind_at"])

        if remind_at <= now:
            await send_reminder(bot, reminder["id"], reminder["user_id"], reminder["text"])
            skipped += 1
        else:
            schedule_reminder(
                bot=bot,
                scheduler=scheduler,
                reminder_id=reminder["id"],
                user_id=reminder["user_id"],
                text=reminder["text"],
                remind_at=remind_at,
            )
            restored += 1

    logger.info(f"Restored {restored} jobs, sent {skipped} overdue reminders")
    