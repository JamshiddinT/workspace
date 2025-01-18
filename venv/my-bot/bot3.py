import logging
import asyncio
import sqlite3
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from weather import register_weather_handlers
from register import register_handlers
# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
api_key = os.getenv("API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    """)
    conn.commit()
    conn.close()


@dp.message(Command(commands=["start", "help"]))
#@dp.message(lambda message: message.text.lower() == "/start")
async def send_welcome(message: types.Message):
    #await message.reply("Welcome! You are authorized. Choose an option:")
    keyboard=ReplyKeyboardMarkup(keyboard=
        [
            [KeyboardButton(text="weather"), KeyboardButton(text="news🛠")],
            [KeyboardButton(text="currency🛠"), KeyboardButton(text="register")],
            [KeyboardButton(text="dictionary🛠"), KeyboardButton(text="photos🛠")],
        ], 
        resize_keyboard=True
        )

    await message.reply("Welcome! You are authorized. Please, choose an option from menu:", reply_markup=keyboard)

# @dp.callback_query(lambda c: c.data == "callback_data")
# async def handle_callback(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "You clicked the button!")

register_weather_handlers(dp)
register_handlers(dp)

@dp.message()
async def echo(message: Message):
    logging.debug(f"Received message: {message.text}")
    await message.reply(message.text)


@dp.message()
async def echo(message: Message):
    await message.reply(message.text)
    
# Scheduled tasks
async def scheduled_task():
    while True:
        logging.info("Running a scheduled task...")
        await asyncio.sleep(3600)  # Run every hour

@dp.startup()
async def on_startup():
    asyncio.create_task(scheduled_task())
    init_db()
    logging.info("Bot is up and running.")

# Main function
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
