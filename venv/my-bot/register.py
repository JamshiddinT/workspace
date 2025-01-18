import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())


# Define states for FSM
class RegisterStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()

# Start registration
#@dp.message(Command(commands=["register"]))
@dp.message(lambda message: message.text.lower() == "register")
async def start_registration(message: types.Message, state: FSMContext):
    await message.reply("Please enter your first name:")
    await state.set_state(RegisterStates.waiting_for_first_name)

# Collect first name and ask for last name
@dp.message(RegisterStates.waiting_for_first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.reply("Now, please enter your last name:")
    await state.set_state(RegisterStates.waiting_for_last_name)

# Collect last name and save to the database
@dp.message(RegisterStates.waiting_for_last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    first_name = user_data["first_name"]
    last_name = message.text

    # Save data to the database
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
    cursor.execute("""
    INSERT OR IGNORE INTO user (id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    """, (message.from_user.id, message.from_user.username, first_name, last_name))
    conn.commit()
    # Retrieve saved data
    cursor.execute("SELECT username, first_name, last_name FROM user WHERE id = ?", (message.from_user.id,))
    user_info = cursor.fetchone()
    conn.close()

    if user_info:
        username, saved_first_name, saved_last_name = user_info
        await message.reply(
            f"Registration successful!\n\nHere is the information we saved:\n"
            f"Username: {username or 'N/A'}\n"
            f"First Name: {saved_first_name}\n"
            f"Last Name: {saved_last_name}"
        )
    else:
        await message.reply("An error occurred while retrieving your information.")
    
    await state.clear()

# Handle unexpected inputs during the FSM process
@dp.message()
async def unexpected_input(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await message.reply("I didn't understand that. Please follow the registration process.")

def register_handlers(dp: Dispatcher):
    dp.message.register(start_registration, lambda message: message.text.lower() == "register")
    dp.message.register(get_first_name, RegisterStates.waiting_for_first_name)
    dp.message.register(get_last_name, RegisterStates.waiting_for_last_name)
    dp.message.register(unexpected_input)  # Catch-all for FSM process
