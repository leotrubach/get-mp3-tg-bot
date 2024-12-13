import asyncio
import logging
import sys
from os import getenv
import dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandObject
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from get_song_mp3_bot.storage.memory import MemoryList
from get_song_mp3_bot.storage.constants import max_reults

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = MemoryList()

dp = Dispatcher()


@dp.message(Command("start"))
async  def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Этот бот может скачать MP3-файл с любого видео, введя название видео с помощью команды `/get название ролика`. После этого вам нужно выбрать с помощью команды `/num число от 1 до 3`.")

@dp.message(Command("get"))

async def get_choice(message: Message, command: CommandObject):
    query =  command.args
    if not query :
        await message.answer("Вы не написали название")
    await message.answer("Ищу видео . . .")
    user_id = message.from_user.id
    urls_list, name_video = storage.get_urls(query, user_id)
    ccc = {}
    for i in range(len(name_video)):
        ccc[name_video[i]] = urls_list[i]
    urls_list = [f"[{name}]({url})" for  name , url  in ccc.items()]
    urls_str = "\n".join([f"{i}. {item}" for i, item in enumerate(urls_list, 1 )])
    print(urls_str)
    await message.answer(f"Выбирете 1 из предложеных ссылок: \n{urls_str}", parse_mode="Markdown" )


@dp.message(Command("num"))

async def choice(message: Message, command: CommandObject):
    num = command.args
    if not num:
        await message.answer("Вы не указали цыфру")
    try:
        if not (1 <= int(num) <= max_reults):
            await message.answer(f"Выберете число от 1 до {max_reults}")
            return
    except ValueError:
        await  message.answer("Укажите цыфру")
        return

    user_id = message.from_user.id
    num = int(num)
    try:
        await message.answer("Загружаю . . .")
        name_video = storage.get_download(num,user_id)

    except KeyError:
        await message.answer("ОШИБКА. Сначало введите что хотите скачать `/get название ролика`")
        return
    path = f"C:/Users/Гала/PycharmProjects/get_song_mp3_bot/youtube_audio/{name_video}.mp3"
    audio = BufferedInputFile.from_file(path=path, filename=f"{name_video}.mp3")
    await bot.send_audio(chat_id=message.chat.id ,audio=audio)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())