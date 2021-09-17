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

def eval_quiz(update, context, correct_option_ids, corret_answer_text, wrong_answer_text):
    update = update["poll_answer"]
    
    if update.option_ids == [correct_option_ids]:
        update.user.send_message(corret_answer_text.format(name=context.user_data["name"]),
                                reply_markup=ReplyKeyboardRemove())
    else:
        update.user.send_message(wrong_answer_text.format(name=context.user_data["name"]),
                                reply_markup=ReplyKeyboardRemove())


action_functions = {"eval_quiz": eval_quiz
                    }