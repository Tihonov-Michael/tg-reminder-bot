import asyncio
import logging
from datetime import datetime, timezone

import dateparser
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.keyboards.reply import cancel_menu, main_menu
from bot.states import ReminderStates
from db.queries import add_reminder, delete_reminder, get_reminders
from scheduler.jobs import schedule_reminder

logger = logging.getLogger(__name__)
router = Router()

MAX_REMINDER_TEXT_LENGTH = 500

geolocator = Nominatim(user_agent="tg-reminder-bot")
tf = TimezoneFinder()


async def resolve_timezone(city: str) -> str | None:
    try:
        location = await asyncio.to_thread(
            geolocator.geocode, city, language="ru", timeout=5
        )
        if not location:
            return None
        tz_name = await asyncio.to_thread(
            tf.timezone_at, lat=location.latitude, lng=location.longitude
        )
        return tz_name
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logger.error(f"Geocoder error for city '{city}': {e}")
        return None


# --- Отмена ---

@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu())


# --- Город / часовой пояс ---

@router.message(F.text == "⚙️ Мой город")
async def ask_city(message: Message, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_city)
    await message.answer(
        "🏙 Напиши название своего города — я определю часовой пояс автоматически.\n\n"
        "Например: <b>Казань</b>, <b>Владивосток</b>, <b>Москва</b>",
        reply_markup=cancel_menu(),
        parse_mode="HTML",
    )


@router.message(ReminderStates.waiting_for_city)
async def set_city(message: Message, state: FSMContext):
    city = message.text.strip()

    if len(city) > 100:
        await message.answer("⚠️ Слишком длинное название. Попробуй ещё раз.")
        return

    tz_name = await resolve_timezone(city)

    if not tz_name:
        await message.answer(
            "⚠️ Не удалось определить часовой пояс для этого города.\n"
            "Проверь название и попробуй ещё раз."
        )
        return

    await state.update_data(timezone=tz_name, city=city)
    await state.set_state(None)
    await message.answer(
        f"✅ Город установлен: <b>{city}</b>\n"
        f"🕐 Часовой пояс: <b>{tz_name}</b>",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    logger.info(f"User {message.from_user.id} set city '{city}', timezone '{tz_name}'")


# --- Создание напоминания ---

@router.message(F.text == "➕ Новое напоминание")
async def new_reminder_start(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data.get("timezone"):
        await state.set_state(ReminderStates.waiting_for_city)
        await message.answer(
            "Сначала укажи свой город — это нужно один раз 👇\n\n"
            "Например: <b>Казань</b>, <b>Владивосток</b>, <b>Москва</b>",
            reply_markup=cancel_menu(),
            parse_mode="HTML",
        )
        return

    await state.set_state(ReminderStates.waiting_for_text)
    await message.answer(
        "📝 Введи текст напоминания:",
        reply_markup=cancel_menu(),
    )


@router.message(ReminderStates.waiting_for_text)
async def reminder_text_received(message: Message, state: FSMContext):
    text = message.text.strip()

    if len(text) > MAX_REMINDER_TEXT_LENGTH:
        await message.answer(
            f"⚠️ Текст слишком длинный. Максимум {MAX_REMINDER_TEXT_LENGTH} символов."
        )
        return

    await state.update_data(reminder_text=text)
    await state.set_state(ReminderStates.waiting_for_time)
    await message.answer(
        "⏰ Когда напомнить? Например:\n"
        "• <i>завтра в 15:00</i>\n"
        "• <i>через 2 часа</i>\n"
        "• <i>25 мая в 10:30</i>",
        reply_markup=cancel_menu(),
        parse_mode="HTML",
    )


@router.message(ReminderStates.waiting_for_time)
async def reminder_time_received(message: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    data = await state.get_data()
    tz_name = data.get("timezone", "UTC")
    reminder_text = data.get("reminder_text")

    parsed_time = dateparser.parse(
        message.text,
        languages=["ru", "en"],
        settings={
            "TIMEZONE": tz_name,
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
        },
    )

    if not parsed_time:
        await message.answer(
            "⚠️ Не удалось распознать время. Попробуй ещё раз.\n\n"
            "Примеры:\n"
            "• <i>завтра в 15:00</i>\n"
            "• <i>через 2 часа</i>\n"
            "• <i>25 мая в 10:30</i>",
            parse_mode="HTML",
        )
        return

    now = datetime.now(timezone.utc)
    if parsed_time <= now:
        await message.answer("⚠️ Это время уже прошло. Укажи время в будущем.")
        return

    remind_at_utc = parsed_time.astimezone(timezone.utc)
    reminder_id = await add_reminder(
        user_id=message.from_user.id,
        text=reminder_text,
        remind_at=remind_at_utc.isoformat(),
        timezone=tz_name,
    )

    bot = message.bot
    schedule_reminder(
        bot=bot,
        scheduler=scheduler,
        reminder_id=reminder_id,
        user_id=message.from_user.id,
        text=reminder_text,
        remind_at=remind_at_utc.replace(tzinfo=None),
    )

    await state.clear()
    await state.update_data(timezone=tz_name)

    local_time = parsed_time.strftime("%d.%m.%Y в %H:%M")
    await message.answer(
        f"✅ Напоминание установлено!\n\n"
        f"📝 {reminder_text}\n"
        f"⏰ {local_time} ({tz_name})",
        reply_markup=main_menu(),
    )
    logger.info(f"User {message.from_user.id} set reminder {reminder_id} at {remind_at_utc}")


# --- Список напоминаний ---

@router.message(F.text == "📋 Мои напоминания")
async def list_reminders(message: Message, state: FSMContext):
    reminders = await get_reminders(message.from_user.id)

    if not reminders:
        await message.answer(
            "У тебя нет активных напоминаний.\n"
            "Нажми ➕ чтобы создать первое!",
            reply_markup=main_menu(),
        )
        return

    lines = ["📋 <b>Твои напоминания:</b>\n"]
    for r in reminders:
        remind_at = datetime.fromisoformat(r["remind_at"])
        formatted = remind_at.strftime("%d.%m.%Y в %H:%M")
        lines.append(f"🔔 <b>#{r['id']}</b> — {formatted} (UTC)\n{r['text']}\n")

    lines.append("Чтобы удалить — напиши <b>/delete_ID</b>, например <b>/delete_5</b>")
    await message.answer("\n".join(lines), reply_markup=main_menu(), parse_mode="HTML")


# --- Удаление напоминания ---

@router.message(F.text.regexp(r"^/delete_\d+$"))
async def delete_reminder_handler(message: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    reminder_id = int(message.text.split("_")[1])
    deleted = await delete_reminder(reminder_id, message.from_user.id)

    if not deleted:
        await message.answer("⚠️ Напоминание не найдено или уже удалено.")
        return

    try:
        scheduler.remove_job(str(reminder_id))
    except Exception:
        pass

    await message.answer(f"✅ Напоминание #{reminder_id} удалено.", reply_markup=main_menu())
    logger.info(f"User {message.from_user.id} deleted reminder {reminder_id}")
    