from telegram import ReplyKeyboardRemove

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