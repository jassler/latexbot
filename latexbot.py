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
import latextopng

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello, me bot is and i lov u <3")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="sry can't help yet")


def inline_latex(update, context):
    """Handle latex query"""
    try:
        # technically this should throw an exception if query is empty (I think (maybe))
        query = update.inline_query.query

        # filenames for the images
        # we generate 3 images
        # - inline1.png for the original
        # - inline1.jpg to send
        # - thumb_inline1.jpg to show thumbnail (20x20 pixels)
        name = 'inline{}'.format(inline_latex.counter)
        inline_latex.counter += 1

        img_png = '{}.png'.format(name)
        img_jpg = '{}.jpg'.format(name)

        # format query
        # should we do input checking?
        # ...
        # nah
        source = r'${}$'.format(query)

        # technically latex_to_image should return False if something went wrong during compilation
        if not latextopng.latex_to_image(source, img_png):
            update.inline_query.answer([InlineQueryResultArticle(id=uuid4(),title="Input invalid", input_message_content=source)])
            return

        # put jpgs somewhere where Telegram can find it through a url
        # since I'm using Flask, images are put int the static folder
        img_path = 'static/img/latex'
        subprocess.call(['gm', 'convert', img_png, '{}/{}'.format(img_path, img_jpg)])
        subprocess.call(['gm', 'convert', '{}/{}'.format(img_path, img_jpg), '-resize', '20x20!', '{}/thumb_{}'.format(img_path, img_jpg)])

        # show the one and only image!
        results = [
            InlineQueryResultPhoto(
                id=uuid4(),
                photo_url='{}/img/latex/{}'.format(config.URL, img_jpg),
                thumb_url='{}/img/latex/thumb_{}'.format(config.URL, img_jpg)),
            ]

        update.inline_query.answer(results)

    except:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title="Gimme yo LaTeX",
            input_message_content="."
            )]
inline_latex.counter = 0

def error(update, context):
    """Does it log errors? I don't know!"""
    logger.warning('Update "{}" caused error "{}"'.format(update, context.error))


def create_latex(update, context):
    """General chat conversation with the bot.
    Any message sent here gets turned into LaTeX, whether you like it or not"""

    resp = context.bot.send_message(chat_id=update.effective_chat.id, text='One moment...', disable_notification=True)

    try:
        # create unique and special name for our special user
        name = '{}.png'.format(create_latex.counter)
        create_latex.counter += 1

        # turn query to png
        source = r'${}$'.format(update.message.text)
        latextopng.latex_to_image(source, name)

        # send png
        chat_id = update.effective_chat.id
        b = context.bot
        b.send_photo(chat_id=chat_id, photo=open(name, 'rb'))

        # convert to webp file so we can send is as a sticker
        latextopng.resize(name, to_webp=True)
        b.send_sticker(chat_id=chat_id, sticker=open(Path(name).with_suffix('.webp'), 'rb'))

        os.remove(name)
        os.remove(Path(name).with_suffix('.webp'))
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Something went wrong, this probably is your fault')

    # delete the "please wait" message
    resp.delete()

create_latex.counter = 0


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

    # start bot
    updater.start_polling()
    updater.idle()
