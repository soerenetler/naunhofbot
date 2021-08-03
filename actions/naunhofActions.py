from telegram import (ParseMode, InputFile, InputMediaPhoto, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update, CallbackQuery)
from telegram.ext import CallbackContext, ConversationHandler
from PIL import Image
import re

import base64
from io import BytesIO
import yaml

from actions import utils

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def save_name(update, context):
    context.user_data["name"] = update.message.from_user.first_name
    context.user_data["daten"] = True

def eval_schaetzfrage_bahnhof(update, context):
    update.message.reply_text("Let's seee",
            reply_markup=ReplyKeyboardRemove())

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

    echter_hour = 0
    echter_minute = 59
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

def eval_quiz(update, context, correct_option_ids, corret_answer_text, wrong_answer_text):
    update = update["poll_answer"]
    
    if update.option_ids == [correct_option_ids]:
        user = context.user_data["name"] 
        update.user.send_message('Richtig, {user} 🎉'.format(name=context.user_data["name"]),
                                reply_markup=ReplyKeyboardRemove())
    else:
        update.user.send_message('Nicht ganz!'.format(name=context.user_data["name"]),
                                reply_markup=ReplyKeyboardRemove())


action_functions = {"save_name": save_name,
                    "eval_schaetzfrage_bahnhof": eval_schaetzfrage_bahnhof
                    }