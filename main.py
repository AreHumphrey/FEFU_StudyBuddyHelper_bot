import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
SUBSCRIPHED_DISCIPLINES_MESSAGE = "Выбери дисциплину по которой можешь помочь студентам, указав ее номер в списке:\n"
for i, discipline in enumerate(DISCIPLINES):
    SUBSCRIPHED_DISCIPLINES_MESSAGE += f"{i + 1}. {discipline}\n"

CHANGE_DISCIPLINES_MESSAGE = "Измени дисциплину по которой можешь помочь студентам, написав ее в формате:\nПоменяй на №"
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
        "<b>Привет!</b>\nДля более продуктивного обучения в ДВФУ был создан этот телеграмм-бот, позволяющий находить ответы на интересующие вопросы, помогать другим студентам в обучении по дисциплинам, которые тебе хорошо знакомы, искать людей, желающих организовывать учебные/внеучебные кружки.\nНадеемся ты найдешь, то что искал! ",
        parse_mode=ParseMode.HTML,
        reply_markup=SUBSCRIBED_DISCIPLINES_KEYBOARD)

@dp.message(lambda message: message.text == "Подать заявку")
async def request_help(message: types.Message):
    user_id = message.from_user.id

    await message.reply("Вы хотите подать заявку? Выберите дисциплину по которой будет ваша заявка:\n" + SUBSCRIPHED_DISCIPLINES_MESSAGE)

@dp.message(lambda message: message.text.startswith("№"))
async def choose_discipline_for_request(message: types.Message):
    user_id = message.from_user.id
    try:
        discipline_number = int(''.join(filter(str.isdigit, message.text)))
        if discipline_number < 1 or discipline_number > len(DISCIPLINES):
            raise ValueError
    except ValueError:
        await message.reply("Неверный формат ввода. Пожалуйста, укажите номер дисциплины из списка.")
        return

    discipline = DISCIPLINES[discipline_number - 1]
    await message.reply("Напишите текст заявки:")

    # Save the chosen discipline for the user
    user = User.get_or_none(user_id=user_id)
    if user:
        user.subscribed_disciplines = discipline
        user.save()
        db.commit()

@dp.message(lambda message: message.text)
async def save_request_text(message: types.Message):
    user_id = message.from_user.id
    request_text = message.text

    await message.reply("Введите свой ник в телеграмме:")

    user = User.get_or_none(user_id=user_id)
    if user:
        user_request = HelpRequest(user_id=user_id, discipline=user.subscribed_disciplines, request_link=request_text, anonymous=False)
        user_request.save()
        db.commit()

@dp.message(lambda message: message.text.startswith("Поменяй на №"))
async def change_disciplines(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        discipline_number = int(''.join(filter(str.isdigit, message.text)))
        if discipline_number < 1 or discipline_number > len(DISCIPLINES):
            raise ValueError
    except ValueError:
        await message.reply("Неверный формат ввода. Пожалуйста, укажите номер дисциплины из списка.", reply_markup=ACTIONS_KEYBOARD)
        return

    new_discipline = DISCIPLINES[discipline_number - 1]
    user = User.get_or_none(user_id=user_id)
    if user:
        user.subscribed_disciplines = new_discipline
        user.save()
        db.commit()
        await message.reply(f"Дисциплина поменялась на:\n <b>{new_discipline}</b>", reply_markup=ACTIONS_KEYBOARD)
    else:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте еще раз.", reply_markup=ACTIONS_KEYBOARD)

@dp.message(lambda message: message.text == "Выбрать свою дисциплину" or any(char.isdigit() for char in message.text))
async def show_disciplines_list(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if message.text == "Выбрать свою дисциплину":
        await message.reply(SUBSCRIPHED_DISCIPLINES_MESSAGE)
    elif any(char.isdigit() for char in message.text):
        selected_disciplines = [int(i.split('.')[0]) for i in message.text.split('\n') if i[0].isdigit()]
        disciplines = [DISCIPLINES[idx - 1] for idx in selected_disciplines if 1 <= idx <= 19]

        if len(disciplines) == 0:
            await message.reply(
                "Пожалуйста, выбери дисциплины, используя цифры, соответствующие номеру желаемой дисциплины")
            return

        disciplines_str = ', '.join(disciplines)
        user = \
            User.get_or_create(user_id=user_id, username=username,
                               defaults={'subscribed_disciplines': disciplines_str})[0]
        user.save()
        db.commit()
        formatted_disciplines = ", ".join(disciplines)
        await message.reply(
            f"Выбрана дисциплина:\n<b>{formatted_disciplines}</b>.\nТеперь ты сможешь помогать другим студентам тоже в ней разобраться\nКоманды которыми ты можешь воспользоваться:\n<b>Подать заявку</b> - ты сможешь попросить помощи у студентов по необходимой дисциплине",
            parse_mode=ParseMode.HTML,
            reply_markup=ACTIONS_KEYBOARD
        )


@dp.message(lambda message: message.text == "Изменить свою дисциплину")
async def show_disciplines_list(message: types.Message):
    await message.reply(CHANGE_DISCIPLINES_MESSAGE, reply_markup=ACTIONS_KEYBOARD)




async def send_request_notifications(user_id: int, subscribed_discipline: str):
    # Retrieve help requests for the subscribed discipline
    help_requests = HelpRequest.select().where(HelpRequest.discipline == subscribed_discipline)

    if help_requests:
        # Iterate over each help request and send a notification message to the user
        for request in help_requests:
            # Format the notification message with the help request text and the telegram username
            notification_text = f"Заявка по вашей дисциплине:\n\n{request.request_link} / {request.user_id}"

            # Send the notification message to the user
            await bot.send_message(user_id, notification_text)
    else:
        # If no help requests found for the subscribed discipline, notify the user
        await bot.send_message(user_id, "Пока нет заявок по вашей дисциплине.")
@dp.message(lambda message: message.text)
async def save_request_text(message: types.Message):
    user_id = message.from_user.id
    request_text = message.text

    await message.reply("Введите свой ник в телеграмме:")

    # Save the request text for the user
    user = User.get_or_none(user_id=user_id)
    if user:
        user_request = HelpRequest(user_id=user_id, discipline=user.subscribed_disciplines, request_link=request_text, anonymous=False)
        user_request.save()
        db.commit()

        # Send request notifications to users subscribed to the same discipline
        await send_request_notifications(user_id, user.subscribed_disciplines)  # Add this line
@dp.message(lambda message: message.text)
async def save_request_text(message: types.Message):
    user_id = message.from_user.id
    request_text = message.text

    await message.reply("Введите свой ник в телеграмме:")

    # Save the request text for the user
    user = User.get_or_none(user_id=user_id)
    if user:
        user_request = HelpRequest(user_id=user_id, discipline=user.subscribed_disciplines, request_link=request_text, anonymous=False)
        user_request.save()
        db.commit()

        # Send request notifications to users subscribed to the same discipline
        await send_request_notifications(user_id, user.subscribed_disciplines)

        # Send a reply to the user
        await message.reply("Спасибо за вашу заявку! Ожидайте ответа.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
