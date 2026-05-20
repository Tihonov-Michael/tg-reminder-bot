from dotenv import load_dotenv
import os

load_dotenv()

print(repr(os.getenv("BOT_TOKEN")))

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")