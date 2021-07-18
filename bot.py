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

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,PicklePersistence, 
                          ConversationHandler, CallbackQueryHandler, PollAnswerHandler, PollHandler, TypeHandler)

from digitalguide.generateActions import Action, read_action_yaml, callback_query_handler

from actions import naunhofActions, generalActions

from configparser import ConfigParser
import argparse

import os
import sys
import traceback
from threading import Thread

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read Telegram Token')
    parser.add_argument('telegram_token', type=str,
                        help='the telegram token for your bot')

    args = parser.parse_args()

    import os

    TOKEN = args.telegram_token
    PORT = int(os.environ.get('PORT', '8080'))

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update: Update, context: CallbackContext):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    def error_handler(update: Update, context: CallbackContext):
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)


    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    my_persistence = PicklePersistence(filename='../bot_persistence')
    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    naunhofActions = read_action_yaml("actions/naunhof.yml", action_functions=naunhofActions.action_functions)
    generalActions = read_action_yaml("actions/general.yml", action_functions=generalActions.action_functions)
    cqh = callback_query_handler({**naunhofActions})

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout = 6 * 60 * 60, 
        entry_points=[CommandHandler('start', naunhofActions["intro"])],
        persistent=True,
        name='naunhofbot',

        states={
            "INTRO": [CommandHandler('weiter', naunhofActions["frage_bahnhof"])],

            "FRAGE_BAHNHOF": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_bahnhof_aufloesung"])],

            "FRAGE_BAHNHOF_AUFLOESUNG": [CommandHandler('weiter', naunhofActions["frage_bahnhof"])],

            "ROUTEN_AUSWAHL": [CommandHandler('city', naunhofActions["city_route_start"]),
                               CommandHandler('see', naunhofActions["see_route_start"])],

            "WEG_SKATEPARK": [CommandHandler('weiter', naunhofActions["frage_bahnhof"])],

            "FRAGE_SKATEPARK": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_skatepark_aufloesung"])],

            "FRAGE_SKATEPARK_AUFLOESUNG": [CommandHandler('weiter', naunhofActions["weg_parkplatz"])],

            "WEG_PARKPLATZ": [CommandHandler('weiter', naunhofActions["weg_stadtgut"])],

            "WEG_STADTGUT": [CommandHandler('weiter', naunhofActions["eis_stadtgut"])],

            "EIS_STADTGUT": [CommandHandler('weiter', naunhofActions["frage_stadtgut"])],

            "FRAGE_STADTGUT": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_stadtgut2"])],

            "FRAGE_STADTGUT2": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["weg_marktplatz"])],

            "WEG_MARKTPLATZ": [CommandHandler('weiter', naunhofActions["frage_marktplatz"])],

            "FRAGE_MARKTPLATZ": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_marktplatz2"])],

            "FRAGE_MARKTPLATZ2": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["rathaus"])],

            "RATHAUS": [CommandHandler('weiter', naunhofActions["weg_oase"])],

            "WEG_OASE": [CommandHandler('weiter', naunhofActions["weg_oase2"])],

            "WEG_OASE2": [CommandHandler('weiter', naunhofActions["stadtteile"])],

            "STADTTEILE": [CommandHandler('weiter', naunhofActions["weg_kita"])],

            "WEG_KITA": [CommandHandler('weiter', naunhofActions["frage_kita"])],

            "FRAGE_KITA": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_kita_aufloesung"])],

            "FRAGE_KITA_AUFLOESUNG": [CommandHandler('weiter', naunhofActions["gymnasium"])],

            "GYMNASIUM": [CommandHandler('weiter', naunhofActions["feuerwehr"])],

            "FEUERWEHR": [CommandHandler('weiter', naunhofActions["parthelandhalle"])],

            "PARTHELANDHALLE": [CommandHandler('weiter', naunhofActions["waldbad"])],

            "WALDBAD": [CommandHandler('weiter', naunhofActions["parthe"])],

            "PARTHE": [CommandHandler('weiter', naunhofActions["weg_schlossturmplatz"])],

            "WEG_SCHLOSSTURMPLATZ": [CommandHandler('weiter', naunhofActions["frage_schlossturmplatz"])],

            "FRAGE_SCHLOSSTURMPLATZ": [MessageHandler(Filters.text & ~Filters.command, naunhofActions["frage_schlossturmplatz_aufloesung"])],

            "FRAGE_SCHLOSSTURMPLATZ_AUFLOESUNG": [CommandHandler('weiter', naunhofActions["ende"])],

            ConversationHandler.TIMEOUT: [MessageHandler(Filters.regex(r'^(.)+'), naunhofActions["timeout"])],
        },

        fallbacks=[CommandHandler('cancel', generalActions["cancel"]),
                   CommandHandler('start', generalActions["start_name"]),
                   CallbackQueryHandler(cqh),
                   CommandHandler('restart', restart, filters=Filters.user(username='@soeren101')),
                   CommandHandler('restart', restart, filters=Filters.user(username='@aehryk')),
                   TypeHandler(Update, generalActions["log_update"])]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)


    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url="https://naunhofbot-szuep.ondigitalocean.app/" + TOKEN)
    updater.idle()
