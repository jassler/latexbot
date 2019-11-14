#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, ParseMode, InputTextMessageContent
from telegram.utils.helpers import escape_markdown
from threading import Thread
from pathlib import Path
from uuid import uuid4
import latextopng
import subprocess
import traceback
import random
import logging
import shutil
import time

import os

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello, me bot is and i lov u <3")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="sry can't help yet")

def start_countdown(seconds, response, update, context):
    while seconds > 0:
        time.sleep(1)
        seconds -= 1
        response.edit_text(str(seconds))

    context.bot.send_message(chat_id=update.effective_chat.id, text="VIRUS AAAAH")

# Currently in use
def love(update, context):
    msg: str = update.message.text
    try:
        int(msg)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Me no take numbers no more, only want love")
    except:
        count = msg.lower().count("love")
        if count < 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Me not see love in your message 😢")
        else:
            love = "❤️💞😘😍🥰💝💟💗💖"
            for _ in range(0, count):
                l = str(random.SystemRandom().choice(love))
                context.bot.send_message(chat_id=update.effective_chat.id, text=l)

def echo(update, context):
    """If number is sent, it start a countdown"""
    msg = update.message.text
    try:
        num = int(msg)
        if num < 1:
            # number too low
            context.bot.send_message(chat_id=update.effective_chat.id, text="Zahl muss mindestens 1 sein")
        else:
            # success! start countdown
            resp = context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            Thread(target=start_countdown, args=(num,resp,update,context)).start()
    except:
        # didn't receieve an int
        context.bot.send_message(chat_id=update.effective_chat.id, text="bitte gib mir zahl danke")

# Currently in use
def inlinequery(update, context):
    """Handle the inline query."""
    try:
        query = update.inline_query.query
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Caps",
                input_message_content=InputTextMessageContent(
                    query.upper())),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Bold",
                input_message_content=InputTextMessageContent(
                    "*{}*".format(escape_markdown(query)),
                    parse_mode=ParseMode.MARKDOWN)),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Italic",
                input_message_content=InputTextMessageContent(
                    "_{}_".format(escape_markdown(query)),
                    parse_mode=ParseMode.MARKDOWN))]

        update.inline_query.answer(results)
    except:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title="Don't forget your text",
            input_message_content=None
            )]

def inline_latex(update, context):
    """Handle latex query"""
    try:
        query = update.inline_query.query
        name = 'inline{}'.format(inline_latex.counter)
        inline_latex.counter += 1

        img_png = '{}.png'.format(name)
        img_jpg = '{}.jpg'.format(name)

        source = r'${}$'.format(query)
        if not latextopng.latex_to_image(source, img_png):
            update.inline_query.answer([InlineQueryResultArticle(id=uuid4(),title="Input invalid")])
            return

        img_path = 'static/img/latex'
        subprocess.call(['gm', 'convert', img_png, '{}/{}'.format(img_path, img_jpg)])
        subprocess.call(['gm', 'convert', '{}/{}'.format(img_path, img_jpg), '-resize', '20x20!', '{}/thumb_{}'.format(img_path, img_jpg)])

        results = [
            InlineQueryResultPhoto(
                id=uuid4(),
                photo_url='https://kaasbrot.com/img/latex/{}'.format(img_jpg),
                thumb_url='https://kaasbrot.com/img/latex/thumb_{}'.format(img_jpg)),
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
    logger.warning('Update "{}" caused error "{}"'.format(update, context.error))

def create_latex(update, context):

    resp = context.bot.send_message(chat_id=update.effective_chat.id, text='One moment...', disable_notification=True)

    try:
        name = '{}.png'.format(create_latex.counter)
        create_latex.counter += 1

        source = r'${}$'.format(update.message.text)
        latextopng.latex_to_image(source, name)

        chat_id = update.effective_chat.id
        b = context.bot
        b.send_photo(chat_id=chat_id, photo=open(name, 'rb'))


        latextopng.resize(name, to_webp=True)
        b.send_sticker(chat_id=chat_id, sticker=open(Path(name).with_suffix('.webp'), 'rb'))


        # os.remove(name)
        # os.remove(Path(name).with_suffix('.webp'))
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Something went wrong, this probably is your fault')
    resp.delete()

create_latex.counter = 0


# TELEGRAM SETUP
if __name__ == '__main__':
    updater = Updater(token='960820032:AAG9sH9Wmv5BYVTz2QmLHQk3hasFc2c9GRo', use_context=True)

    dp = updater.dispatcher

    # basic functions
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(MessageHandler(Filters.text, create_latex))

    # inline
    dp.add_handler(InlineQueryHandler(inline_latex))

    # error handling
    dp.add_error_handler(error)

    # start bot
    updater.start_polling()
    updater.idle()
