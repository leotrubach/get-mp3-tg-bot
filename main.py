import asyncio
import logging
import os
import pathlib
import sys
import uuid
from os import getenv

import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types import Message

from data.storage.memory import MemoryList

dotenv.load_dotenv()

TOKEN = getenv("BOT_TOKEN")
PATH_VIDEO = pathlib.Path(os.getenv("PATH_VIDEO"))

PATH_AUDIO = pathlib.Path(os.getenv("PATH_AUDIO"))

session = AiohttpSession(
    api=TelegramAPIServer.from_base(base="http://telegram-bot-api:8081", is_local=True)
)
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    session=session,
)

storage = MemoryList()

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Этот бот может скачать MP3-файл с любого видео, введя название видео с помощью команды `/get название ролика`. После этого вам нужно выбрать что хотите скачать."
    )


@dp.message(Command("q"))
async def get_choice(message: Message):
    path = PATH_VIDEO / "0bcb946f-2ce7-4586-8481-9bc7d09b2617.mp3"
    if os.path.isfile(path):
        print("Папка существует")
    else:
        print("Папка не существует")
    print(path)
    await bot.send_video(chat_id=message.chat.id, video=path.absolute().as_uri())


@dp.message(Command("video"))
async def get_video(message: Message, command: CommandObject):
    user_id = message.from_user.id
    url = command.args
    result_uuid = str(uuid.uuid4())
    x = storage.get_video(url, user_id, result_uuid)
    buttons = [
        [InlineKeyboardButton(text=i, callback_data=f"videores/{result_uuid}/{str(i)}")]
        for i in x
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        f"Выбирете 1 из предложеных качеств:",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@dp.message(Command("get"))
async def get_choice(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Вы не написали название")
        return
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

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer(
        f"Выбирете 1 из предложеных ссылок: \n{urls_str}",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@dp.message()
async def download_by_url(message: Message):
    result_uuid = str(uuid.uuid4())
    url = message.text

    storage.get_download_url(url, result_uuid)

    path = PATH_AUDIO / f"{result_uuid}.mp3"

    await bot.send_audio(chat_id=message.chat.id, audio=path.absolute().as_uri())


@dp.callback_query()
async def callback_handler(callback_query: types.CallbackQuery):
    data = callback_query.data
    scope, reply_uuid, btn_id = data.split("/")
    user_id = callback_query.from_user.id
    if scope == "search":
        await callback_query.message.answer("Загружаю . . .")
        name_video = storage.get_download(reply_uuid, user_id)
        path = PATH_AUDIO / f"{reply_uuid}.mp3"
        await bot.send_audio(
            chat_id=callback_query.message.chat.id, audio=path.absolute().as_uri()
        )
    if scope == "videores":
        await callback_query.message.answer("Загружаю . . .")
        name_video = storage.get_download_video(btn_id, reply_uuid, user_id)
        if name_video == "Размер файла больше 2000мб":
            await bot.send_message(
                chat_id=callback_query.message.chat.id, text=name_video
            )
            return
        path = PATH_VIDEO / f"{reply_uuid}"

        await bot.send_video(
            chat_id=callback_query.message.chat.id, video=path.absolute().as_uri()
        )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
