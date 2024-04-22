import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import TOKEN
from models import User, HelpRequest, db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

DISCIPLINES = [
    'Высшая математика',
    'Программмирование',
    'Физика',
    'Химия',
    'Биология',
    'Английский язык',
    'Восточные языки',
    'Экономика',
    'Механика',
    'География',
    'Гуманитарные науки',
    'Право',
    'Медицина',
    'Проектная деятельность',
    'Дизайн и графическое искусство',
    'Психология',
    'Креативное письмо и журналистика',
    'Здоровье и физическая культура',
    'Внеучебные организации'
]
SUBSCRIPHED_DISCIPLINES_MESSAGE = "Выберите дисциплину по которой можете помочь студентам:\n"
for i, discipline in enumerate(DISCIPLINES):
    SUBSCRIPHED_DISCIPLINES_MESSAGE += f"{i + 1}. {discipline}\n"

SUBSCRIBED_DISCIPLINES_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Выбрать свою дисциплину")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Для более продуктивного обучения в ДВФУ был создан этот телеграмм-бот, позволяющий находить ответы на на интересующие вопросы, помогать другим студентам в обучении по дисциплинам, которые тебе хорошо знакомы, искать людей, желающих организовывать учебные/внеучебные кружки. Надеемся ты найдешь, то что искал! ",

        reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)


dp.message()
async def show_disciplines_list(message: types.Message):
    await message.reply(SUBSCRIPHED_DISCIPLINES_MESSAGE, reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)

@dp.message()
async def update_subscribed_disciplines(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if message.text == "Выбрать свою дисциплину":
        await message.reply(SUBSCRIPHED_DISCIPLINES_MESSAGE, reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)
    else:
        disciplines = [DISCIPLINES[int(i.split('.')[0]) - 1] for i in message.text.split('\n') if i[0].isdigit()]

        user = User.get_or_create(user_id=user_id, username=username, defaults={'subscribed_disciplines': disciplines})[0]
        user.save()
        db.commit()

        await message.reply("Дисциплины успешно обновлены.")


@dp.message()
async def create_help_request(message: types.Message):
    user_id = message.from_user.id
    discipline = message.text
    request_link = f"https://t.me/{message.from_user.username}"

    help_request = HelpRequest.get_or_create(user_id=user_id, discipline=discipline, request_link=request_link,
                                             defaults={'anonymous': False})[0]
    help_request.save()

    await message.reply(f"Заявка на помощь в дисциплине {discipline} успешно создана. Ваша ссылка: {request_link}")


@dp.message()
async def change_disciplines(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    user = User.get(User.user_id == user_id)
    current_disciplines = set(user.subscribed_disciplines.split(','))

    for discipline in DISCIPLINES:
        if discipline not in current_disciplines:
            button = KeyboardButton(discipline)
            SUBSCRIBED_DISCIPLINES_KEYBOARD.add(button)

    await message.reply("Пожалуйста, выберите дисциплины, которые вы хотите изменить.",
                        reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
