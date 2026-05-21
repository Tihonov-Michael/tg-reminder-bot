# 🔔 Telegram Бот-Напоминалка

[🇬🇧 Read in English](README.md)

Telegram-бот для установки напоминаний на естественном языке. Портфолио-проект, демонстрирующий чистую архитектуру, асинхронный Python и профессиональные практики разработки ботов.

## Возможности

- 📝 Напоминания на естественном языке — *"завтра в 15:00"*, *"через 2 часа"*, *"25 мая в 10:30"*
- 🌍 Автоматическое определение часового пояса по названию города
- 📋 Просмотр и управление активными напоминаниями
- 🔄 Напоминания сохраняются после перезапуска бота
- 🛡 Защита от спама, валидация данных, защита от SQL-инъекций

## Стек

| Инструмент | Назначение |
|------------|-----------|
| [aiogram 3](https://docs.aiogram.dev/) | Асинхронный фреймворк для Telegram Bot API |
| [APScheduler](https://apscheduler.readthedocs.io/) | Планировщик задач |
| [SQLite + aiosqlite](https://aiosqlite.omnilib.dev/) | Асинхронная локальная база данных |
| [dateparser](https://dateparser.readthedocs.io/) | Парсинг дат на естественном языке |
| [geopy](https://geopy.readthedocs.io/) + [timezonefinder](https://timezonefinder.readthedocs.io/) | Определение часового пояса по городу |

## Структура проекта

```
reminder_bot/
├── bot/
│   ├── handlers/
│   │   ├── start.py          # /start, /help
│   │   └── reminders.py      # FSM: создание, список, удаление
│   ├── middlewares/
│   │   └── throttling.py     # Защита от спама
│   ├── keyboards/
│   │   └── reply.py          # Клавиатуры
│   └── states.py             # Состояния FSM
├── db/
│   ├── database.py           # Подключение, инициализация
│   └── queries.py            # SQL-запросы
├── scheduler/
│   └── jobs.py               # Задачи APScheduler
├── config.py                 # Конфигурация из .env
└── main.py                   # Точка входа
```

## Запуск

### Требования

- Python 3.11+
- Токен бота от [@BotFather](https://t.me/BotFather)

### Установка

1. Клонируй репозиторий:
```bash
git clone https://github.com/Tihonov-Michael/tg-reminder-bot.git
cd tg-reminder-bot
```

2. Создай и активируй виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux / macOS
```

3. Установи зависимости:
```bash
pip install -r requirements.txt
```

4. Создай файл `.env`:
```
BOT_TOKEN=your_token_here
```

5. Запусти бота:
```bash
python main.py
```

## Безопасность

- Все запросы к БД используют параметризованные выражения — защита от SQL-инъекций
- Rate limiting через middleware — защита от спама
- Данные пользователей строго изолированы по `user_id`
- Токен бота хранится в `.env`, исключён из системы контроля версий

## Лицензия

MIT
