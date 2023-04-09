import os
import re
import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv, find_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook


load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO)


WEBHOOK_HOST = 'https://your.domain'
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = os.environ.get("WEBAPP_HOST")
WEBAPP_PORT = os.environ.get("WEBAPP_PORT")


bot = Bot(token=os.environ.get("API_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class User_():
    username: str
    user_nickname: str or None
    user_photo_url: str or None
    user_email: str
    user_phone: str or None
    user_password: str

    def send_data(self):
        try:
            requests.post(f'{os.environ.get("DJANGO_URL")}/register/', json={"username": self.username,
                                                               "user_nickname": self.user_nickname,
                                                               "image_url": self.user_photo_url,
                                                               "email": self.user_email,
                                                               "user_phone": self.user_phone,
                                                               "password": self.user_password,
                                                               }, timeout=10)
            return True
        except:
            return False


class AnswerUser(StatesGroup):
    answer = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(f"Hello {message.from_user.username}! For register in Django app input command /register")


@dp.message_handler(commands=['register'])
async def register(message: types.Message, state: FSMContext):
    user_ = User_()
    user_photo_url = await bot.get_user_profile_photos(message.from_user.id)
    try:
        file = await bot.get_file(user_photo_url.photos[0][0].file_id)
        user_.user_photo_url = str(bot.get_file_url(file.file_path))
    except:
        user_.user_photo_url = None
    user_.user_nickname = message.from_user.first_name
    user_.username = message.from_user.username or user_.user_nickname
    await AnswerUser.answer.set()
    async with state.proxy() as data:
        data['user_'] = user_
    await message.reply(f"For register in Django app send message in format:\n"
                        f"example@gmail.com/+380934048404/your_password")



@dp.message_handler(state=AnswerUser.answer)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        user_ = data['user_']
        mes_ = user_message
        if re.search(r"^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}/\+\d{10,}/[a-zA-Z0-9!()-]+$", mes_):
            mes_ = mes_.split('/')
            user_.user_email, user_.user_phone, user_.user_password = mes_[0], mes_[1], mes_[2]
            if user_.send_data():
                await message.reply(f"Register ok\n"
                                    f"Your login: {user_.username}\n"
                                    f"Your password: {user_.user_password}\n"
                                    f"Link to Django app: {os.environ.get('DJANGO_URL')}")
            else:
                await message.reply(f"Something with Django app")
        else:
            await message.reply(f"Check your data in message")
            await register(message, state)
    await state.finish()


async def on_startup(dp):
    logging.info('Starting...')
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    logging.info('Shutting down...')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )