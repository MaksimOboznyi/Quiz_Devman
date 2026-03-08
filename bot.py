import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv


load_dotenv()

TG_TOKEN = os.getenv('TG_BOT_TOKEN')

def strat(update, context):
    update.message.reply_text("Здравствуйте")
    

def echo(update, context):
    user_message = update.message.text
    update.message.reply_text(user_message)
    

def main():
    updater = Updater(TG_TOKEN, use_context=True)
    
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start', strat))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    updater.start_polling()
    updater.idle()
    

if __name__ == '__main__':
    main()