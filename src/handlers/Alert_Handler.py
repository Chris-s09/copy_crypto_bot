from telegram import InlineKeyboardMarkup, Bot
from src.config.config import BOT_TOKEN
from src.db_connection.connectionpg import DatabaseManager 
import asyncio 
import random
import string
import time
from src.helpers.common_instances import bot
async def sendMessage(text: str, tgId: int, reply_markup =None):
  """
  sends a message to a telegram user
  """
  try:
    if not isinstance(text, str):
      raise TypeError(f"Expected a string for the message but got {type(text)}")
    if not isinstance(tgId, int):
      raise TypeError(f"Expected an integer for the telegram id but got {type(tgId)}")
    if reply_markup and not isinstance(reply_markup, InlineKeyboardMarkup):
      raise TypeError(f"Expected a InlineKeyboardMarkup for the reply_markup but got {type(reply_markup)}")

    await bot.send_message(chat_id=tgId, text=text,reply_markup = reply_markup, parse_mode='MarkdownV2')
  except TypeError as e:
    print(f"Type error in sendMessage: {e}")
  except Exception as e:
    print(f'Unable to send message to bot:{BOT_TOKEN} Error:', e)

def get_tg_ids_by_moniter_wallet(wallet: str) -> list:
    """
    Returns a list of telegram ids of users who are monitoring a wallet.
    """
    try:
        client = DatabaseManager()
        res = client.get_tgid_by_moniter_wallet(wallet_address=wallet)
        if res is None:
            return []
        return [data[0].get('telegram_id') for data in res if data and data[0]]
    except AttributeError as e:
        # Handle null pointer references
        print(f"AttributeError in get_tg_ids_by_moniter_wallet: {e}")
        return []
    except Exception as e:
        # Handle unhandled exceptions
        print(f"An error occurred in get_tg_ids_by_moniter_wallet: {e}")
        return []
  


class AlertManager:
  _instance = None

  def __init__(self):
      self.alert_id_data = {}

  @classmethod
  def default(cls):
      """Static method to get the singleton instance."""
      if cls._instance is None:
          cls._instance = cls()
      return cls._instance

  def set(self, id, value):
      if id is None:
          raise ValueError("id cannot be None")
      if value is None:
          raise ValueError("value cannot be None")

      self.alert_id_data[id] = value

  def get(self, id):
      if id is None:
          raise ValueError("id cannot be None")
      return self.alert_id_data.get(id, None)
  
  def generate_random_id(self, length=10):
        if length is None or length < 0:
            raise ValueError("length cannot be None or negative")
        # Generate a random alphanumeric string of specified length
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(letters_and_digits) for i in range(length))
        return result_str
     
  
  async def clear_id_after_delay(self, id, delay=300):
      if id is None:
          raise ValueError("id cannot be None")
      if delay is None or delay < 0:
          raise ValueError("delay cannot be None or negative")
      if id in self.alert_id_data:
          await asyncio.sleep(delay)

          del self.alert_id_data[id]

alert_manager = AlertManager().default()