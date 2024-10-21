# BOT_TOKEN = "7347500058:AAG6iBqMw6n1-XYZEh9NW6kAtj_dLAyCNak" production
BOT_TOKEN = "7650950112:AAHqsiuXEGcfFn73lToCQn_ZqB9xL6bNewQ"  # @chris_local_bot local
# BOT_TOKEN = "7858566449:AAFUlULH3NCffxDU1ZzQAyWrp501BYb9HJg" #@chris_crypto_bot staging
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = b"DhAjnKnt8rqDZhpJV5NnMbHnF4rzsVXZmHlhzICj03g="
SOLANA_URL = "https://api.mainnet-beta.solana.com"
BIRD_EYE_API_KEY = "979df75b18664b468cf303427c2bd9e7"
SWAP_FEES = 0.05
PLATFORM_WALLET = "8BXWz5VkCGkALYSsDrC6s9fnCfXpw89uJEN6pntY9A1c"
MOON_PAY_API_KEY = ""
ENVIRONMENT = "dev"  # dev | prod
SELL_PRECENTAGE = 0.10
DEBUGGING = True
SOLSCAN_WALLET_URL = "https://solscan.io/account/{wallet_address}" # Change this with 
MOONPAY_DEPOSIT_URL = f"https://buy.moonpay.com/?apiKey={MOON_PAY_API_KEY}&currencyCode=SOL&walletAddress={PLATFORM_WALLET}"

# if not all([
#     BOT_TOKEN,
#     SOLANA_URL,
#     BIRD_EYE_API_KEY,
#     SECRET_KEY,
#     SWAP_FEES,
#     PLATFORM_WALLET,
#     ENVIRONMENT,
#     SELL_PRECENTAGE
# ]):
#     raise Exception("Some env variables are not set")
