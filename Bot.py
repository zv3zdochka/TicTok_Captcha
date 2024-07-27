import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import F

TOKEN = "7268777414:AAHhRoVk8v2HiOaiy0yzind2I3Llg7fqci8"
users = set()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
wait_flag = False
oper_found = False
selected = 0
link = ''
denied = []


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.chat.id not in users:
        users.add(message.chat.id)
        update_json()
    await message.answer(f"Hello, {hbold(message.from_user.full_name)} !\nWaiting for CAPTCHA.")


def update_json():
    try:
        with open('users.json', 'w') as f:
            data = {'users': list(users)}
            json.dump(data, f)
    except Exception as e:
        exit(e)


@dp.message(F.text.lower() == "да")
async def yes(message: types.Message):
    global wait_flag, oper_found, selected, link
    if wait_flag:
        await message.reply(link, reply_markup=types.ReplyKeyboardRemove())
        wait_flag = False
        oper_found = True
        selected = message.chat.id
        await deny()
    else:
        await message.reply("Кто-то уже выбрал эту капчу.", reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == "нет")
async def no(message: types.Message):
    await message.reply("Хорошо", reply_markup=types.ReplyKeyboardRemove())
    denied.append(message.chat.id)


async def deny():
    for user_id in users:
        if user_id != selected and user_id not in denied:
            await bot.send_message(user_id, "Эту капчу уже заняли", reply_markup=types.ReplyKeyboardRemove())


async def call_users():
    global wait_flag
    text = "Вы сейчас готовы решить капчу?"
    kb = [
        [
            types.KeyboardButton(text="Да"),
            types.KeyboardButton(text="Нет")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    try:
        with open('users.json', 'r', errors='ignore') as file:
            data = json.load(file)
            for user_id in data.get('users', []):
                users.add(user_id)
    except FileNotFoundError:
        pass

    for user_id in users:
        await bot.send_message(user_id, text, reply_markup=keyboard)
    wait_flag = True


async def checker():
    global oper_found
    while not oper_found:
        await asyncio.sleep(1)
    return True


async def main():
    await call_users()
    check_task = asyncio.create_task(checker())
    poll_task = asyncio.create_task(dp.start_polling(bot))
    done, pending = await asyncio.wait(
        [check_task, poll_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    return check_task.result()


async def call_operator(text: str):
    global link
    link = text
    return await main()
