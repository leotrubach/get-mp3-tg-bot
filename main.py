import asyncio
import logging
import sys
from os import getenv

import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, BufferedInputFile

from get_song_mp3_bot.storage.constants import max_reults
from get_song_mp3_bot.storage.memory import MemoryList

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = MemoryList()

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Этот бот может скачать MP3-файл с любого видео, введя название видео с помощью команды `/get название ролика`. После этого вам нужно выбрать что хотите скачать.")

@dp.message(Command("get"))
async def get_choice(message: types.Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Вы не написали название")
    await message.answer("Ищу видео . . .")
    user_id = message.from_user.id
    urls_list, name_video = storage.get_urls(query, user_id)
    ccc = {}
    for i in range(len(name_video)):
        ccc[name_video[i]] = urls_list[i]
    urls_list = [f"[{name}]({url})" for name, url in ccc.items()]
    urls_str = "\n".join([f"{i}. {item}" for i, item in enumerate(urls_list, 1)])
    print(urls_str)
    buttons = [
        [InlineKeyboardButton(text=f"{i} ссылка", callback_data=str(i))]
        for i in range(1, max_reults + 1)
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(f"Выбирете 1 из предложеных ссылок: \n{urls_str}", parse_mode="Markdown", reply_markup=keyboard )

@dp.callback_query()
async def callback_handler(callback_query: types.CallbackQuery):
    button_number = callback_query.data
    num = int(button_number)
    user_id = callback_query.from_user.id
    try:
        await callback_query.message.answer("Загружаю . . .")
        name_video = storage.get_download(num, user_id)

    except KeyError:
        await callback_query.message.answer("ОШИБКА. Сначало введите что хотите скачать `/get название ролика`")
        return
    path = f"C:/Users/Гала/PycharmProjects/get_song_mp3_bot/youtube_audio/{name_video}.mp3"
    audio = BufferedInputFile.from_file(path=path, filename=f"{name_video}.mp3")
    await bot.send_audio(chat_id=callback_query.message.chat.id, audio=audio)

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())