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
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession

print("loading models and db...", flush=True)
import db
import sberrag
print("models and db loaded!", flush=True)
TOKEN = getenv("BOT_TOKEN")
SUPERADMIN = getenv("SUPERADMIN")

dp = Dispatcher()

bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))

class Form(StatesGroup):
    id = State()

def isSuperAdmin(id):
    if id == int(SUPERADMIN):
        return True
    return False


# def admin_keyboard(message: Message):
#     print(db.is_admin(message.from_user.id), flush=True)
#     if db.is_admin(message.from_user.id)[0] == 1:
#         kb = [
#             [
#                 KeyboardButton(text="Добавить админа"),
#                 KeyboardButton(text="Добавить статью"),
#                 KeyboardButton(text="Сохранить кэш"),
#             ],
#         ]
#         if isSuperAdmin(message.from_user.id):
#             kb = [
#             [
#                 KeyboardButton(text="Добавить админа"),
#                 KeyboardButton(text="Добавить статью"),
#             ],
#             [
#                 KeyboardButton(text="Сохранить кэш"),
#                 KeyboardButton(text="Удалить админа"),
#             ]
#         ]
#         keyboard = ReplyKeyboardMarkup(
#             keyboard=kb,
#             resize_keyboard=True,
#             input_field_placeholder="Панель администратора"
#         )
#         return keyboard
#     return None


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """
#     This handler receives messages with `/start` command
#     """
#     keyboard = admin_keyboard(message)
#     if isSuperAdmin(message.from_user.id):
#         await message.answer("Вы супер администратор", reply_markup=keyboard)
#     elif db.is_admin(message.from_user.id)[0] == 1:
#         await message.answer("Вы администратор", reply_markup=keyboard)
#     await message.answer(f"Здравствуйте, {html.bold(message.from_user.full_name)}! Я бот-помощник, специализирющийся на научных статьях о нефтегазовой промышленности. Пожалуйста, введите ваш вопрос")

# @dp.message(F.text.lower() == "добавить админа")
# async def add_admin_handler(message: Message) -> None:
#     if db.is_admin(message.from_user.id)[0] == 1:
#         db.add_message(message["message_id"], message.chat.id,
#                         message.text, [])
#         await message.answer("Введите id сессии")
#     else: 
#         await message.answer("Извините, у вас недостаточно прав для этой команды")

# @dp.message(F.text.lower() == "удалить админа")
# async def add_doc_handler(message: Message) -> None:
#     if isSuperAdmin(message.from_user.id):
#         db.add_message(message["message_id"], message.chat.id,
#                         message.text, [])
#         await message.answer("Введите id сессии")
#     else: 
#         await message.answer("Извините, у вас недостаточно прав для этой команды")

# @dp.message(F.text.lower() == "добавить статью")
# async def add_doc_handler(message: Message) -> None:
#     if db.is_admin(message.from_user.id)[0] == 1:
#         db.add_message(message["message_id"], message.chat.id,
#                         message.text, [])
#         await message.answer("Отправьте статью")
#     else: 
#         await message.answer("Извините, у вас недостаточно прав для этой команды")


# @dp.message(F.text.lower() == "сохранить кэш")
# async def save_faiss(message: Message) -> None:
#     if db.is_admin(message.from_user.id)[0] == 1:
#         db.add_message(message["message_id"], message.chat.id,
#                         message.text, [])
#         sberrag.save_faiss()
#         await message.answer("Кэш сохранен")
#     else: 
#         await message.answer("Извините, у вас недостаточно прав для этой команды")

# @dp.message(Command("get_chat_id"))
# async def get_chat_id_handler(message: Message) -> None:
#     await message.answer(f"<code>{message.chat.id}</code>")

async def echo_handler(message) -> None:
    # try:
    #     if db.is_admin(message["user_id"])[0] == 1 and db.get_previous_message(message.chat.id) == 'Добавить админа':
    #         db.add_admin(int(message.text))
    #         await message.answer("Админ добавлен")
    #         db.add_message(message["message_id"], message.chat.id,
    #                 message.text, [])
    #     elif db.is_admin(message["user_id"])[0] == 1 and db.get_previous_message(message.chat.id) == 'Добавить статью':
    #         await sberrag.add_document(message.document.file_id, message.document.file_name)
    #         await message.answer("Статья добавлена")
    #         db.add_message(message["message_id"], message.chat.id,
    #                 message.text, [])
    #     elif isSuperAdmin(message["user_id"]) and db.get_previous_message(message.chat.id) == 'Удалить админа':
    #         try:
    #             db.delete_admin(int(message.text))
    #             await message.answer("Админ удален")
    #         except Exception as e:
    #             print(e, flush=True)
    #             await message.answer("Ошибка удаления админа, попробуйте снова")
    #         db.add_message(message["message_id"], message["chat_id"],
    #                 message.text, [])
    #     else:
    # keyboard = admin_keyboard(message)
    # builder = InlineKeyboardBuilder()
    # for i in range(4):
    #     builder.add(InlineKeyboardButton(
    #         text="Источник " + str(i + 1),
    #         callback_data="ref_" + str(i + 1))
    #     )
    answer = sberrag.answer_sbert(message)
    db.add_message(randint(0,1000000), randint(0,1000000),
                    message, [])
    return f"""
        <b>Вот что я думаю по вашему вопросу:</b>\n\n{answer["answer"]}\n\n<b>Возможно вам будут полезны следующие источники:</b>"""
    # await message.answer(f"""
    #     <b>Вот что я думаю по вашему вопросу:</b>\n\n{answer["answer"]}\n\n<b>Возможно вам будут полезны следующие источники:</b>""",
    #                         reply_markup=builder.as_markup())
    # except TypeError as e:
    #     print(e, flush=True)
    #     await message.answer("Извините, я вас не понимаю, попробуйте переформулировать вопрос")


# @dp.callback_query(F.data.split("_")[0] == "ref")
# async def send_ref(callback: CallbackQuery):
#     n = int(callback.data.split("_")[1])
#     ref = db.get_ref(callback.message["message_id"] - 1, callback.message.chat.id, n)
#     try:
#         await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message["message_id"] + 1, text = f"""
#             <b>Источник:</b> <code>{ref[1]}</code>\n\n<blockquote>{ref[0]}</blockquote>""")
#     except Exception as e:
#         if str(e) != "Telegram server says - Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message":
#             await callback.message.answer(f"""
#                 <b>Источник:</b> <code>{ref[1]}</code>\n\n<blockquote>{ref[0]}</blockquote>""")



# async def main() -> None:
    
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#     db.migrate_postgres(SUPERADMIN)
#     asyncio.run(main())
