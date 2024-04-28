import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
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

DISCIPLINES_MESSAGE = "Выбери дисциплину:\n"
for i, discipline in enumerate(DISCIPLINES):
    DISCIPLINES_MESSAGE += f"{i + 1}. {discipline}\n"

SUBSCRIPHED_DISCIPLINES_MESSAGE = "Выбери дисциплину по которой можешь помочь студентам, указав ее номер в списке:\n"
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
        ],
        [
            KeyboardButton(text="Посмотреть заявки")
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


@dp.message(lambda message: message.text == "Посмотреть заявки")
async def handle_view_requests(message: types.Message):
    user_id = message.from_user.id
    user = User.get_or_none(user_id=user_id)
    if user:
        active_requests = HelpRequest.select().where(HelpRequest.discipline == user.subscribed_disciplines)

        for request in active_requests:
            author_contacts = f"Контакты автора заявки:\n"
            user = User.get_or_none(user_id=request.user_id)
            if user:
                if user.username:
                    author_contacts += f"Username: @{user.username}\n"

            await bot.send_message(request.user_id, f"Появилась новая заявка по вашей выбранной дисциплине!\n\n"
                                                    f"Текст заявки:\n\n {request.request_link}\n\n"
                                                    f"{author_contacts}", reply_markup=ACTIONS_KEYBOARD)


@dp.message(lambda message: message.text == "Подать заявку")
async def request_help(message: types.Message):
    user_id = message.from_user.id

    await message.reply(
        "Вы хотите подать заявку? Выберите дисциплину по которой будет ваша заявка:\n" + DISCIPLINES_MESSAGE + "\nУкажи номер дисциплины в формате  <b>№(1-19)</b>", parse_mode=ParseMode.HTML)


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

    user = User.get_or_none(user_id=user_id)
    if user:
        user.subscribed_disciplines = discipline
        user.save()
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
        await message.reply("Неверный формат ввода. Пожалуйста, укажите номер дисциплины из списка.",
                            reply_markup=ACTIONS_KEYBOARD)
        return

    new_discipline = DISCIPLINES[discipline_number - 1]
    user = User.get_or_none(user_id=user_id)
    if user:
        user.subscribed_disciplines = new_discipline
        user.save()
        db.commit()
        await message.reply(f"Дисциплина поменялась на:\n<b>{new_discipline}</b>", reply_markup=ACTIONS_KEYBOARD,
                            parse_mode=ParseMode.HTML, )
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
            f"Выбрана дисциплина:\n<b>{formatted_disciplines}</b>.\nТеперь ты сможешь помогать другим студентам тоже в ней разобраться\nКоманды которыми ты можешь воспользоваться:\n<b>Подать заявку</b> - ты сможешь попросить помощи у студентов по необходимой дисциплине \n <b>Изменить свою дисциплину</b> - ты можешь поменять дисциплину в которой разбираешься, воспользовавшись этой командой",
            parse_mode=ParseMode.HTML,
            reply_markup=ACTIONS_KEYBOARD
        )


@dp.message(lambda message: message.text == "Изменить свою дисциплину")
async def show_disciplines_list(message: types.Message):
    await message.reply(DISCIPLINES_MESSAGE + "Напиши сообщение в формате:\n <b>Поменяй на №</b>", reply_markup=ACTIONS_KEYBOARD,  parse_mode=ParseMode.HTML,)


@dp.message(lambda message: message.text)
async def save_request_and_nickname(message: types.Message):
    user_id = message.from_user.id
    user = User.get_or_none(user_id=user_id)
    if not user:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        return

    user_request = HelpRequest(user_id=user_id, discipline=user.subscribed_disciplines,
                               request_link=message.text,
                               anonymous=True)
    user_request.save()
    db.commit()
    await message.reply(f"Спасибо за вашу заявку!\n\nТекст заявки: {user_request.request_link}\n\nОжидайте ответа.",
                        reply_markup=ACTIONS_KEYBOARD)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
