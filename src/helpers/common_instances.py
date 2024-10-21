
from telegram import Bot
from src.config.config import BOT_TOKEN, SOLANA_URL
from src.db_connection.connectionpg import DatabaseManager
from solana.rpc.api import Client

bot = Bot(token=BOT_TOKEN)
solanaClient = Client(SOLANA_URL)
db_manager = DatabaseManager()
