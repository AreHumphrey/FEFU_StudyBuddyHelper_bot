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
SUBSCRIPHED_DISCIPLINES_MESSAGE = "Выбери дисциплину по которой можешь помочь студентам:\n"
for i, discipline in enumerate(DISCIPLINES):
    SUBSCRIPHED_DISCIPLINES_MESSAGE += f"**{i + 1}.** {discipline}\n"

SUBSCRIBED_DISCIPLINES_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Выбрать свою дисциплину")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

ACTIONS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подать заявку"),
            KeyboardButton(text="Изменить свою дисциплину")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет!\n Для более продуктивного обучения в ДВФУ был создан этот телеграмм-бот, позволяющий находить ответы на на интересующие вопросы, помогать другим студентам в обучении по дисциплинам, которые тебе хорошо знакомы, искать людей, желающих организовывать учебные/внеучебные кружки.\n Надеемся ты найдешь, то что искал! ",

        reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)


@dp.message()
async def show_disciplines_list(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if message.text == "Выбери свою дисциплину, указав ее номер в списке":
        await message.reply(SUBSCRIPHED_DISCIPLINES_MESSAGE, reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)
    elif any(char.isdigit() for char in message.text):
        selected_disciplines = [int(i.split('.')[0]) for i in message.text.split('\n') if i[0].isdigit()]
        disciplines = [DISCIPLINES[idx - 1] for idx in selected_disciplines if 1 <= idx <= 19]

        if len(disciplines) == 0:
            await message.reply(
                "Пожалуйста, выбери дисциплины, используя цифры, соответсвующие номеру желаемой дисциплины")
            return

        user = User.get_or_create(user_id=user_id, username=username, defaults={'subscribed_disciplines': disciplines})[
            0]
        user.save()
        db.commit()

        return await message.reply(
            f"Выбрана дисциплина: {disciplines}.\n Теперь ты сможешь помогать другим студентам тоже в ней разобраться\nКоманды которыми ты можешь воспользоваться:\n*Подать заявку* - ты сможешь попросить помощи у студентов по необходимой дисциплине",
            reply_markup=ACTIONS_KEYBOARD)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
