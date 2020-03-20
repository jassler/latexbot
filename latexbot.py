#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, ParseMode, InputTextMessageContent

from threading import Thread
from pathlib import Path
from uuid import uuid4
import subprocess
import logging
import os

# python files in same folder
import config
import mathrenderer

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

img_path = 'static/img'

# functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello, me bot is and i lov u <3")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="sry can't help yet")


def inline_latex(update, context):
    """Handle inline latex query
    Very buggy at the moment"""

    try:
        # technically this should throw an exception if query is empty (I think (maybe))
        query = update.inline_query.query

        name = 'inline{}.jpg'.format(inline_latex.counter)
        inline_latex.counter += 1
        if inline_latex.counter > 9999:
            inline_latex.counter = 0

        img_jpg = os.path.join(img_path, name)
        mathrenderer.render_latex(img_jpg, query)

        # show the one and only image!
        results = [InlineQueryResultPhoto(
                id=uuid4(),
                title='Ready to ship',
                thumb_url='{}/img/smallsuccess.png'.format(config.URL, name),
                photo_url='{}/img/{}'.format(config.URL, name))
            ]
        update.inline_query.answer(results)

    except:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title="Gimme yo LaTeX",
            input_message_content=InputTextMessageContent("Malformattet math input"),
            thumb_url='{}/img/smallfail.png'.format(config.URL))
        ]
        update.inline_query.answer(results)

inline_latex.counter = 0


def create_latex(update, context):
    """General chat conversation with the bot.
    Any message sent here gets turned into LaTeX, whether you like it or not"""

    resp = context.bot.send_message(chat_id=update.effective_chat.id, text='One moment...', disable_notification=True)

    try:
        # create unique and special name for our special user
        name = os.path.join(img_path, '{}'.format(create_latex.counter))
        png_name = name + '.png'
        webp_name = name + '.webp'
        create_latex.counter += 1
        if create_latex.counter > 9999:
            create_latex.counter = 0

        mathrenderer.render_latex(png_name, update.message.text, format_='png')

        # send png
        chat_id = update.effective_chat.id
        b = context.bot
        b.send_photo(chat_id=chat_id, photo=open(png_name, 'rb'))

        # convert to webp file so we can send is as a sticker
        mathrenderer.resize(png_name, webp_name=webp_name)
        b.send_sticker(chat_id=chat_id, sticker=open(webp_name, 'rb'))

        os.remove(png_name)
        os.remove(webp_name)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Something went wrong, this probably is your fault')

    # delete the "please wait" message
    resp.delete()
create_latex.counter = 0


def error(update, context):
    """Does it log errors? I don't know!"""
    logger.warning('Update "{}" caused error "{}"'.format(update, context.error))

# TELEGRAM SETUP
if __name__ == '__main__':
    updater = Updater(token=config.TOKEN, use_context=True)

    dp = updater.dispatcher

    # basic functions
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    # chat message handler
    dp.add_handler(MessageHandler(Filters.text, create_latex))

    # inline
    dp.add_handler(InlineQueryHandler(inline_latex))

    # error handling
    dp.add_error_handler(error)
    print("Start polling")
    # start bot
    updater.start_polling()
    updater.idle()
