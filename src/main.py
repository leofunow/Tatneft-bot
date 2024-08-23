import asyncio
import logging
import psycopg2
import sys
from os import getenv
from random import randint

from aiogram import F
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Здравствуйте, {html.bold(message.from_user.full_name)}! Я бот-помощник, специализирющийся на научных статьях о нефтегазовой промышленности. Пожалуйста, введите ваш вопрос")


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        builder = InlineKeyboardBuilder()
        for i in range(randint(1, 3)):
            builder.add(InlineKeyboardButton(
                text="Источник " + str(i + 1),
                callback_data="ref_" + str(i + 1))
            )
        await message.answer(f"""
            <b>Вот что я думаю по вашему вопросу:</b>\n\n{message.text}""",
            reply_markup=builder.as_markup())
    except TypeError:
        await message.answer("Извините, я вас не понимаю, попробуйте переформулировать вопрос")


@dp.callback_query(F.data.split("_")[0] == "ref")
async def send_ref(callback: CallbackQuery):
    await callback.message.answer(f"""
        <b>Источник:</b> Ссылка на источник {callback.data.split("_")[1]}\n\n<blockquote>бла бла бла</blockquote>""")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    db.migrate_postgres()
    asyncio.run(main())

