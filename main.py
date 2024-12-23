import asyncio
import logging
import sys
import uuid
from os import getenv

import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.types import Message

from get_song_mp3_bot.storage.memory import MemoryList

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

storage = MemoryList()

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Этот бот может скачать MP3-файл с любого видео, введя название видео с помощью команды `/get название ролика`. После этого вам нужно выбрать что хотите скачать."
    )


#
# @dp.message(Command("video"))
# async def get_video(message: Message, command: CommandObject):
#     url = command.args
#     x = storage.get_videoe(url)
#     print(x)
#     buttons = [[InlineKeyboardButton(text=i, callback_data=str(i))] for i in x]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#
#     await message.answer(
#         f"Выбирете 1 из предложеных качеств:",
#         parse_mode="Markdown",
#         reply_markup=keyboard,
#     )
#


@dp.message(Command("get"))
async def get_choice(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Вы не написали название")
    await message.answer("Ищу видео . . .")
    user_id = message.from_user.id
    urls_list, name_video, search_results = storage.get_urls(query, user_id)
    search_callbacks = {}
    buttons = []
    for i, result in enumerate(search_results, 1):
        result_uuid = str(
            uuid.uuid4()
        )  # Генерация уникального uuid для каждого результата
        callback_data = f"search/{result_uuid}/{str(i)}"
        print(callback_data, len(callback_data))
        buttons.append(
            InlineKeyboardButton(text=f"{i} ссылка", callback_data=callback_data)
        )
        search_callbacks[result_uuid] = result  # Сохраняем в словарь по uuid
        # Добавляем данные о поисковых результатах в состояние пользователя
    storage.user_state[user_id].search_callbacks.update(search_callbacks)

    ccc = {}
    for i in range(len(name_video)):
        ccc[name_video[i]] = urls_list[i]
    urls_list = [f"[{name}]({url})" for name, url in ccc.items()]
    urls_str = "\n".join([f"{i}. {item}" for i, item in enumerate(urls_list, 1)])
    print(urls_str)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer(
        f"Выбирете 1 из предложеных ссылок: \n{urls_str}",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


# @dp.message()
# async def download_by_url(message: Message):
#     url = message.text
#     name = storage.get_download_url(url)
#     path = f"C:/Users/Гала/PycharmProjects/get_song_mp3_bot/youtube_audio/{name}.mp3"
#     audio = BufferedInputFile.from_file(path=path, filename=f"{name}.mp3")
#     await bot.send_audio(chat_id=message.chat.id, audio=audio)


@dp.callback_query()
async def callback_handler(callback_query: types.CallbackQuery):
    data = callback_query.data
    print(data)
    scope, reply_uuid, btn_id = data.split("/")
    user_id = callback_query.from_user.id
    if scope == "search":
        await callback_query.message.answer("Загружаю . . .")
        name_video = storage.get_download(reply_uuid, user_id)
        path = f"C:/Users/Гала/PycharmProjects/get_song_mp3_bot/youtube_audio/{name_video}.mp3"
        audio = BufferedInputFile.from_file(path=path, filename=f"{name_video}.mp3")
        await bot.send_audio(chat_id=callback_query.message.chat.id, audio=audio)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
