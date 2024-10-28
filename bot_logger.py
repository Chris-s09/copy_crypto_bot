import logging
from telegram import Bot
from datetime import datetime
from src.config.config import LOGGER_BOT_TOKEN
import asyncio
#A logger class in which we have to write the logs locally with time stamp and send the log on telegram bot logger also
# it will make two different functions, one for log locally and other for log on telegram bot

logger_bot = Bot(token=LOGGER_BOT_TOKEN)

class BotLogger:
    def __init__(self):
        self.logger = logging.getLogger('bot_logger')
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler = logging.FileHandler('bot.log')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

# in local we will add time stamp with log
    def local_log(self, message):
        self.logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}')


    def telegram_log(self, message):
        asyncio.create_task(logger_bot.send_message(chat_id='835262237', text=message))

# make a function that if there the change will true in monitor_changes then log else no log
    def log(self, message, local_log=True, telegram_log=True):
        if local_log:
            self.local_log(message)
        if telegram_log:
            self.telegram_log(message)
