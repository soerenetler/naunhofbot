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

from actions import naunhofActions, generalActions
from digitalguide.mongo_persistence import DBPersistence
from digitalguide.errorHandler import error_handler

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

    naunhofActions = read_action_yaml(
        "actions/naunhof.yml", action_functions=naunhofActions.action_functions)
    generalActions = read_action_yaml(
        "actions/general.yml", action_functions=generalActions.action_functions)
    cqh = callback_query_handler({**naunhofActions})

    prechecks = [CommandHandler('cancel', generalActions["cancel"]),
                 CommandHandler('start', generalActions["start_name"]),
                 CallbackQueryHandler(cqh)]

    conv_handler = ConversationHandler(
        allow_reentry=True,
        per_chat=False,
        conversation_timeout=6 * 60 * 60,
        entry_points=[CommandHandler('start', naunhofActions["intro"])],
        persistent=True,
        name='naunhofbot',

        states={
            "INTRO": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_bahnhof"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_BAHNHOF": prechecks+[
                MessageHandler(
                    FilterUhrzeit(), naunhofActions["frage_bahnhof_aufloesung"]),
                TypeHandler(Update, naunhofActions["frage_bahnhof_tipp"])],

            "FRAGE_BAHNHOF_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_bahnhof"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "ROUTEN_AUSWAHL": prechecks+[
                CommandHandler(
                    'city', naunhofActions["city_route_start"]),
                CommandHandler(
                    'see', naunhofActions["see_route_start"]),
                CallbackQueryHandler(cqh),
                TypeHandler(Update, naunhofActions["routen_auswahl_tipp"])],

            "WEG_SKATEPARK": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_bahnhof"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_SKATEPARK": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice) &
                               ~Filters.command, naunhofActions["frage_skatepark_aufloesung"]),
                TypeHandler(Update, naunhofActions["frage_skatepark_tipp"])],

            "FRAGE_SKATEPARK_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["weg_parkplatz"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_PARKPLATZ": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["weg_stadtgut"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["cafe_stadtgut"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "CAFE_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["eis_stadtgut"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "EIS_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_stadtgut"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_STADTGUT": prechecks+[
                PollAnswerHandler(naunhofActions["frage_stadtgut2"]),
                TypeHandler(Update, naunhofActions["frage_stadtgut_tipp"])],

            "FRAGE_STADTGUT2": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice)
                               & ~Filters.command, naunhofActions["frage_stadtgut2_aufloesung"]),
                TypeHandler(Update, naunhofActions["frage_stadtgut2_tipp"])],

            "FRAGE_STADTGUT2_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["weg_marktplatz"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_MARKTPLATZ": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_marktplatz"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_MARKTPLATZ": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice)
                               & ~Filters.command, naunhofActions["frage_marktplatz2"]),
                TypeHandler(Update, naunhofActions["frage_marktplatz_tipp"])],

            "FRAGE_MARKTPLATZ2": prechecks+[
                MessageHandler(
                    (Filters.text | Filters.photo | Filters.voice) & ~Filters.command, naunhofActions["rathaus"]),
                TypeHandler(Update, naunhofActions["frage_marktplatz2_tipp"])],

            "RATHAUS": prechecks+[
                CommandHandler('weiter', naunhofActions["weg_oase"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_OASE": prechecks+[
                CommandHandler('weiter', naunhofActions["weg_oase2"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_OASE2": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["stadtteile"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "STADTTEILE": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["weg_kita"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_KITA": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_kita"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_KITA": prechecks+[
                MessageHandler(
                    Filters.text & ~Filters.command, naunhofActions["frage_kita_aufloesung"]),
                TypeHandler(Update, naunhofActions["frage_kita_tipp"])],

            "FRAGE_KITA_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["gymnasium"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "GYMNASIUM": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["feuerwehr"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FEUERWEHR": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["parthelandhalle"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "PARTHELANDHALLE": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["waldbad"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WALDBAD": prechecks+[
                CommandHandler('weiter', naunhofActions["parthe"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "PARTHE": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["weg_schlossturmplatz"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "WEG_SCHLOSSTURMPLATZ": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["frage_schlossturmplatz"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            "FRAGE_SCHLOSSTURMPLATZ": prechecks+[
                MessageHandler(Filters.regex(
                    EMOJI_PATTERN) & ~Filters.command, naunhofActions["frage_schlossturmplatz_aufloesung"]),
                TypeHandler(Update, naunhofActions["frage_schlossturmplatz_tipp"])],

            "FRAGE_SCHLOSSTURMPLATZ_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', naunhofActions["ende"]),
                TypeHandler(Update, naunhofActions["weiter_tipp"])],

            ConversationHandler.TIMEOUT: [TypeHandler(Update, naunhofActions["timeout"])],
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
