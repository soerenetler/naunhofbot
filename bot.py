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
        "actions/general.yml", action_functions=generalActions.action_functions)
    cqh = callback_query_handler({**cityrouteActions})

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
            "INTRO": prechecks+[
                CommandHandler(
                    'weiter', generalActions["frage_bahnhof"]),
                TypeHandler(Update, generalActions["weiter_tipp"])],

            "FRAGE_BAHNHOF": prechecks+[
                MessageHandler(
                    FilterUhrzeit(), generalActions["frage_bahnhof_aufloesung"]),
                TypeHandler(Update, generalActions["frage_bahnhof_tipp"])],

            "FRAGE_BAHNHOF_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', generalActions["frage_bahnhof"]),
                TypeHandler(Update, generalActions["weiter_tipp"])],

            "ROUTEN_AUSWAHL": prechecks+[
                CommandHandler(
                    'city', cityrouteActions["city_route_start"]),
                CommandHandler(
                    'see', generalActions["see_route_start"]),
                CallbackQueryHandler(cqh),
                TypeHandler(Update, generalActions["routen_auswahl_tipp"])],

            "WEG_SKATEPARK": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["frage_bahnhof"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FRAGE_SKATEPARK": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice) &
                               ~Filters.command, cityrouteActions["frage_skatepark_aufloesung"]),
                TypeHandler(Update, cityrouteActions["frage_skatepark_tipp"])],

            "FRAGE_SKATEPARK_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_parkplatz"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_PARKPLATZ": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_stadtgut"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["cafe_stadtgut"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "CAFE_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["eis_stadtgut"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "EIS_STADTGUT": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["frage_stadtgut"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FRAGE_STADTGUT": prechecks+[
                PollAnswerHandler(cityrouteActions["frage_stadtgut2"]),
                TypeHandler(Update, cityrouteActions["frage_stadtgut_tipp"])],

            "FRAGE_STADTGUT2": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice)
                               & ~Filters.command, cityrouteActions["frage_stadtgut2_aufloesung"]),
                TypeHandler(Update, cityrouteActions["frage_stadtgut2_tipp"])],

            "FRAGE_STADTGUT2_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_marktplatz"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_MARKTPLATZ": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["frage_marktplatz"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FRAGE_MARKTPLATZ": prechecks+[
                MessageHandler((Filters.text | Filters.photo | Filters.voice)
                               & ~Filters.command, cityrouteActions["frage_marktplatz2"]),
                TypeHandler(Update, cityrouteActions["frage_marktplatz_tipp"])],

            "FRAGE_MARKTPLATZ2": prechecks+[
                MessageHandler(
                    (Filters.text | Filters.photo | Filters.voice) & ~Filters.command, cityrouteActions["rathaus"]),
                TypeHandler(Update, cityrouteActions["frage_marktplatz2_tipp"])],

            "RATHAUS": prechecks+[
                CommandHandler('weiter', cityrouteActions["weg_oase"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_OASE": prechecks+[
                CommandHandler('weiter', cityrouteActions["weg_oase2"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_OASE2": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["stadtteile"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "STADTTEILE": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_kita"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_KITA": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_kita2"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_KITA2": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["frage_kita"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FRAGE_KITA": prechecks+[
                MessageHandler(
                    Filters.text & ~Filters.command, cityrouteActions["frage_kita_aufloesung"]),
                TypeHandler(Update, cityrouteActions["frage_kita_tipp"])],

            "FRAGE_KITA_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_gymnasium"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_GYMNASIUM": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["gymnasium"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "GYMNASIUM": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["feuerwehr"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FEUERWEHR": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["parthelandhalle"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "PARTHELANDHALLE": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_waldbad"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_WALDBAD": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["waldbad"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WALDBAD": prechecks+[
                MessageHandler(
                    Filters.text & ~Filters.command, cityrouteActions["waldbad_aufloesung"]),
                TypeHandler(Update, cityrouteActions["waldbad_tipp"])],

            "WALDBAD_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["parthe"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "PARTHE": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["weg_schlossturmplatz"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "WEG_SCHLOSSTURMPLATZ": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["frage_schlossturmplatz"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FRAGE_SCHLOSSTURMPLATZ": prechecks+[
                MessageHandler(Filters.regex(
                    EMOJI_PATTERN) & ~Filters.command, cityrouteActions["frage_schlossturmplatz_aufloesung"]),
                TypeHandler(Update, cityrouteActions["frage_schlossturmplatz_tipp"])],

            "FRAGE_SCHLOSSTURMPLATZ_AUFLOESUNG": prechecks+[
                CommandHandler(
                    'weiter', cityrouteActions["ende"]),
                TypeHandler(Update, cityrouteActions["weiter_tipp"])],

            "FEEDBACK": prechecks+[MessageHandler((Filters.text | Filters.photo | Filters.voice) & ~Filters.command, cityrouteActions["ende_feedback"]),
                        CommandHandler('weiter', cityrouteActions["ende_feedback"]),
                        TypeHandler(Update, cityrouteActions["feedback_tipp"])],

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
