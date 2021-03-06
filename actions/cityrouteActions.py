from telegram import ReplyKeyboardRemove

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def eval_quiz(update, context, correct_option_id, correct_answer_text, wrong_answer_text):
    update = update["poll_answer"]

    if update.option_ids == [correct_option_id]:
        update.user.send_message(correct_answer_text.format(name=context.user_data["name"]),
                                 reply_markup=ReplyKeyboardRemove())
    else:
        update.user.send_message(wrong_answer_text.format(name=context.user_data["name"]),
                                 reply_markup=ReplyKeyboardRemove())


def eval_schaetzfrage_kitas(update, context):
    import re

    schaetzung = int(re.findall(r"\d{1,}", update.message.text)[0])
    echter_wert = 10
    if schaetzung == echter_wert:
        update.message.reply_text('Richtig!',
                                  reply_markup=ReplyKeyboardRemove())

    differenz = schaetzung - echter_wert
    if differenz == -1:
        update.message.reply_text('Es ist eine Kita mehr als du geschätzt hast.',
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz < -1:
        update.message.reply_text('Es sind {} Kitas mehr als du geschätzt hast.'.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz == 1:
        update.message.reply_text('Es ist eine Kita weniger als du geschätzt hast.',
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz > 1:
        update.message.reply_text('Es sind {} Kitas weniger als du geschätzt hast.'.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())


def eval_schaetzfrage_waldbad(update, context):
    import re

    schaetzung = int(re.findall(r"\d{1,}", update.message.text)[0])
    echter_wert = 3200000 
    if schaetzung == echter_wert:
        update.message.reply_text('Richtig!',
                                  reply_markup=ReplyKeyboardRemove())

    differenz = schaetzung - echter_wert
    if differenz != 0:
        differenz_string = '{:,}'.format(abs(differenz)).replace(',', '.')
        update.message.reply_text('Deine Schätzung liegt nur {} Liter daneben.'.format(differenz_string),
                                  reply_markup=ReplyKeyboardRemove())

action_functions = {"eval_quiz": eval_quiz,
                    "eval_schaetzfrage_kitas": eval_schaetzfrage_kitas,
                    "eval_schaetzfrage_waldbad": eval_schaetzfrage_waldbad
                    }
