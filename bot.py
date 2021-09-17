#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence,
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from digitalguide.generateActions import Action, read_action_yaml, callback_query_handler
from digitalguide.uhrzeit_filter import FilterUhrzeit

from actions import cityrouteActions, generalActions
from digitalguide.mongo_persistence import DBPersistence
from digitalguide.generateStates import read_state_yml
from digitalguide.errorHandler import error_handler
from digitalguide import writeActions

from digitalguide.pattern import EMOJI_PATTERN

from configparser import ConfigParser
import argparse

import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    PORT = int(os.environ.get('PORT', '8080'))

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    my_persistence = DBPersistence("naunhofbot_persistencedb")
    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    cityrouteActions = read_action_yaml(
        "actions/cityroute.yml", action_functions={**cityrouteActions.action_functions, **writeActions.action_functions})
    generalActions = read_action_yaml(
        "actions/general.yml", action_functions={**generalActions.action_functions})
    seerouteActions = read_action_yaml(
        "actions/seeroute.yml", action_functions={**writeActions.action_functions})

    cqh = callback_query_handler({**cityrouteActions, **generalActions, **seerouteActions})

    prechecks = [CommandHandler('cancel', generalActions["cancel"]),
                 CommandHandler('start', generalActions["intro"]),
                 CallbackQueryHandler(cqh)]

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout=6 * 60 * 60,
        entry_points=[CommandHandler('start', generalActions["intro"])],
        persistent=True,
        name='naunhofbot',

        states={

            **read_state_yml("states/general.yml", actions={**cityrouteActions, **generalActions, **seerouteActions}, prechecks=prechecks),
            **read_state_yml("states/cityroute.yml", actions={**cityrouteActions}, prechecks=prechecks),

            ConversationHandler.TIMEOUT: [TypeHandler(Update, cityrouteActions["timeout"])],
        },
        fallbacks=[TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=os.environ.get("APP_URL") + TOKEN)
    updater.idle()
