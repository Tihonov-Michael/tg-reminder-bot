# 🔔 Telegram Reminder Bot

[🇷🇺 Читать на русском](README.ru.md)

A Telegram bot that lets users set reminders in natural language. Built as a portfolio project demonstrating clean architecture, async Python, and real-world bot development practices.

## Features

- 📝 Set reminders in natural language — *"tomorrow at 3pm"*, *"in 2 hours"*, *"May 25 at 10:30"*
- 🌍 Automatic timezone detection by city name
- 📋 View and manage active reminders
- 🔄 Reminders survive bot restarts
- 🛡 Rate limiting, input validation, SQL injection protection

## Tech Stack

| Tool | Purpose |
|------|---------|
| [aiogram 3](https://docs.aiogram.dev/) | Async Telegram Bot framework |
| [APScheduler](https://apscheduler.readthedocs.io/) | Job scheduling |
| [SQLite + aiosqlite](https://aiosqlite.omnilib.dev/) | Async local database |
| [dateparser](https://dateparser.readthedocs.io/) | Natural language date parsing |
| [geopy](https://geopy.readthedocs.io/) + [timezonefinder](https://timezonefinder.readthedocs.io/) | City → timezone resolution |

## Project Structure

```
reminder_bot/
├── bot/
│   ├── handlers/
│   │   ├── start.py          # /start, /help
│   │   └── reminders.py      # FSM: create, list, delete
│   ├── middlewares/
│   │   └── throttling.py     # Rate limiting
│   ├── keyboards/
│   │   └── reply.py          # Keyboard layouts
│   └── states.py             # FSM States
├── db/
│   ├── database.py           # Connection, initialization
│   └── queries.py            # SQL queries
├── scheduler/
│   └── jobs.py               # APScheduler jobs
├── config.py                 # Environment config
└── main.py                   # Entry point
```

## Getting Started

### Prerequisites

- Python 3.11+
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your_username/tg-reminder-bot.git
cd tg-reminder-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux / macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
BOT_TOKEN=your_token_here
```

5. Run the bot:
```bash
python main.py
```

## Security

- All database queries use parameterized statements — SQL injection protected
- Rate limiting via middleware — spam protected
- User data is strictly isolated by `user_id`
- Bot token stored in `.env`, excluded from version control

## License

MIT
