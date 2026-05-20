import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import main_menu
from bot.states import ReminderStates

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я помогу тебе не забыть важные дела.\n\n"
        "Что умею:\n"
        "➕ Создавать напоминания\n"
        "📋 Показывать список активных напоминаний\n"
        "🗑 Удалять напоминания\n\n"
        "Выбери действие в меню ниже 👇",
        reply_markup=main_menu(),
    )
    logger.info(f"User {message.from_user.id} started the bot")


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📖 Как пользоваться ботом:\n\n"
        "1. Нажми <b>➕ Новое напоминание</b>\n"
        "2. Введи текст напоминания\n"
        "3. Укажи время — например:\n"
        "   • <i>завтра в 15:00</i>\n"
        "   • <i>через 2 часа</i>\n"
        "   • <i>25 мая в 10:30</i>\n\n"
        "В нужный момент я пришлю тебе сообщение 🔔\n\n"
        "Команды:\n"
        "/start — главное меню\n"
        "/help — эта справка",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    