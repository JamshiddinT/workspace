import logging
from time import sleep
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
api_key = os.getenv("API_KEY")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class WeatherStates(StatesGroup):
    waiting_for_city = State()

#@dp.message(Command(commands=["weather"]))
@dp.message(lambda message: message.text.lower() == "weather")
async def start_weather(message: types.Message, state: FSMContext):
        await message.reply( f"Please enter the name of a city. For example: Tashkent \n \nNote! If you don't get info about weather after sending city name, then the bot should be given admin or message reading right from the group in order to read your message and reply.")
        await state.set_state(WeatherStates.waiting_for_city)

@dp.message(WeatherStates.waiting_for_city)
async def get_weather(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    city = message.text.strip()

    api_key = os.getenv("API_KEY")  # Replace with your actual WeatherAPI key
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"

    async with httpx.AsyncClient() as client:
         response = await client.get(url)
         data = response.json()
    try:
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        await message.reply(f"The temperature in {city} is {temp}°C with {condition}.")
    except KeyError:
        logging.error(f"Unexpected response structure: {response.text}")
        await message.reply("Sorry, the weather data format is not as expected.")
    finally:
        # Clear the state after handling the request
        await state.clear()

def register_weather_handlers(dp: Dispatcher):
    dp.message.register(start_weather, lambda message: message.text.lower() == "weather")
    dp.message.register(get_weather, WeatherStates.waiting_for_city)