# from Constants import API_KEY, logger
from telegram.ext import *
from Responses import *

API_KEY = ''

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

import datetime

print("Bot initiating.......")

def start_command(update, context):
    logger.info(update)
    logger.info(f'for chaid : {update.message.chat.id} message from user :  {update.message.text}')
    response = start_response()
    update.message.reply_text(response)

def help_command(update, context):
    logger.info(update)
    logger.info(f'for chaid : {update.message.chat.id} message from user :  {update.message.text}')
    response = commad_list()
    update.message.reply_text(response)

def stop_command(update, context):
    logger.info(update)
    logger.info(f'for chaid : {update.message.chat.id} message from user :  {update.message.text}')
    response = stop_notification(update.message.chat.id)
    update.message.reply_text(response)

def handle_message(update, context):
    logger.info(update.message)
    text = str(update.message.text).lower()
    chatid = update.message.chat.id
    logger.info(f'for chaid : {update.message.chat.id} message from user :  {text}')
    today = datetime.datetime.now()
    d1 = today.strftime("%d-%m-%Y")
    hello(text, chatid, d1)

def error(update, context):
    print(f"update {update} caused error {context.error}")

def main():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("stop", stop_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()
