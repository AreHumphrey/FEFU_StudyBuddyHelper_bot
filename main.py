from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from telegram.ext import filters
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from models import User, HelpRequest
from peewee import *

db = SqliteDatabase('identifier.sqlite')
db.connect()
db.create_tables([User, HelpRequest])

SUBSCRIBE, CHANGE_SUBSCRIPTION, REQUEST_HELP = range(3)

SUBSCRIBE_CB, CHANGE_SUB_CB, REQUEST_HELP_CB = range(3)


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    User.get_or_create(user_id=user_id, defaults={'username': username})
    update.message.reply_text('Привет! Добро пожаловать в бота помощи. Чем могу помочь?')


def subscribe(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Математика", callback_data=str(SUBSCRIBE_CB)),
         InlineKeyboardButton("Физика", callback_data=str(SUBSCRIBE_CB))],
        [InlineKeyboardButton("Химия", callback_data=str(SUBSCRIBE_CB)),
         InlineKeyboardButton("Информатика", callback_data=str(SUBSCRIBE_CB))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите дисциплины, в которых вы разбираетесь:', reply_markup=reply_markup)
    return SUBSCRIBE


def subscribe_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    subscribed_disciplines = query.data
    User.update(subscribed_disciplines=subscribed_disciplines).where(User.user_id == user_id).execute()
    query.edit_message_text(text=f"Вы подписались на {subscribed_disciplines}")
    return ConversationHandler.END


def change_subscription(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Математика", callback_data=str(CHANGE_SUB_CB)),
         InlineKeyboardButton("Физика", callback_data=str(CHANGE_SUB_CB))],
        [InlineKeyboardButton("Химия", callback_data=str(CHANGE_SUB_CB)),
         InlineKeyboardButton("Информатика", callback_data=str(CHANGE_SUB_CB))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите дисциплины, которые хотите изменить:', reply_markup=reply_markup)
    return CHANGE_SUBSCRIPTION


def change_subscription_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    subscribed_disciplines = query.data
    User.update(subscribed_disciplines=subscribed_disciplines).where(User.user_id == user_id).execute()
    query.edit_message_text(text=f"Вы изменили подписку на {subscribed_disciplines}")
    return ConversationHandler.END


def request_help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Для оставления заявки, пожалуйста, отправьте ссылку на ваш аккаунт.')
    return REQUEST_HELP


def handle_help_request(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    discipline = User.get(User.user_id == user_id).subscribed_disciplines
    request_link = update.message.text
    HelpRequest.create(user_id=user_id, discipline=discipline, request_link=request_link, anonymous=False)
    update.message.reply_text('Заявка успешно отправлена!')
    return ConversationHandler.END


def main():
    updater = Updater("YOUR_BOT_TOKEN")

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SUBSCRIBE: [CallbackQueryHandler(subscribe_callback)],
            CHANGE_SUBSCRIPTION: [CallbackQueryHandler(change_subscription_callback)],
            REQUEST_HELP: [MessageHandler(filters.Text & ~filters.Command, handle_help_request)],
        },
        fallbacks=[CommandHandler('subscribe', subscribe),
                   CommandHandler('change_subscription', change_subscription),
                   CommandHandler('request_help', request_help)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
