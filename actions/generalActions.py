import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
                      Sticker, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

from actions.utils import log

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def save_name(update, context):
    context.user_data["name"] = update.message.from_user.first_name
    context.user_data["daten"] = True

@log(logger)
def log_update(update: Update, context: CallbackContext):
    pass


def return_end(update: Update, context: CallbackContext):
    return ConversationHandler.END

def entry_conversation(update: Update, context: CallbackContext):
    if context.args:
        keyboard = [[InlineKeyboardButton(
            "🐾 los", callback_data='action:' + context.args[0])]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Hi, freut mich, dass du dabei bist! Mit einem klick auf "los" kannst du direkt an die richtige Position in der Route springen',
            reply_markup=reply_markup)
        return None


def eval_schaetzfrage_bahnhof(update, context):
    from ctparse import ctparse

    parse = ctparse(update.message.text, timeout=1).resolution
    schaetzung_minute = parse.minute
    schaetzung_hour = parse.hour

    if schaetzung_hour >= 0 & schaetzung_hour <= 6:
        schaetzung_hour = schaetzung_hour
    elif schaetzung_hour > 6 & schaetzung_hour <= 12:
        schaetzung_hour = schaetzung_hour -12
    elif schaetzung_hour > 12 & schaetzung_hour <= 24:
        schaetzung_hour = schaetzung_hour - 24

    schaetzung_value = schaetzung_hour*60+schaetzung_minute

    echter_hour = 1
    echter_minute = 33
    echter_value = echter_hour*60 + echter_minute
    
    dif_value = echter_value-schaetzung_value

    if dif_value == 0:
        update.message.reply_text('Nicht schlecht! Perfekt getroffen 😉',
            reply_markup=ReplyKeyboardRemove())
    elif dif_value > -60 and dif_value < 60:
        update.message.reply_text('Du liegst weniger als eine Stunde daneben!',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Nicht ganz!',
            reply_markup=ReplyKeyboardRemove())

def default_data(update: Update, context: CallbackContext):
    context.user_data["daten"] = False

def default_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.from_user.first_name

def change_data(update: Update, context: CallbackContext):
    if update.message.text == "Ja" or update.message.text == "Ja, klar 🌻":
        context.user_data["daten"] = True
    else:
        context.user_data["daten"] = False

def change_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text

def pass_func(update: Update, context: CallbackContext):
    pass

action_functions = {"eval_schaetzfrage_bahnhof": eval_schaetzfrage_bahnhof,
                    "save_name": save_name,
                    "change_name": change_name,
                    "change_data": change_data,
                    "default_name": default_name,
                    "default_data": default_data,
                    "entry_conversation": entry_conversation,
                    "return_end": return_end,
                    "pass_func": pass_func}