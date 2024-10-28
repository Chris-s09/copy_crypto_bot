from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from src.db_connection.connectionpg import DatabaseManager
from src.helpers.wallet_generator import create_wallet_address
from src.helpers.constants import MAX_RETRIES
import asyncio
from telegram import Update
from telegram.helpers import escape_markdown
from src.helpers.common_instances import bot, db_manager, solanaClient
from src.helpers.common_helpers import validate_public_key
from solders.pubkey import Pubkey

class My_Wallet_screen_handler:
    # Method to mask the wallet address with stating 3 chars and last 3chars
    @staticmethod
    def mask_wallet_address(wallet_address:str):
        print(wallet_address, type(wallet_address))
        try:
            if wallet_address:
                return f"{wallet_address[:3]}...{wallet_address[-3:]}"
        except Exception as e:
            print(f"Error occurred: {e}")

        return None

    @staticmethod
    async def command_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id

        wallet_address = db_manager.get_wallet_by_telegram_id(user_id)

        keyboard = [
            [
                InlineKeyboardButton(
                    "Create new wallet 🆕", callback_data="/create_new_wallet"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Edit wallet - ({My_Wallet_screen_handler.mask_wallet_address(str(wallet_address))}) 📝",
                    callback_data="/edit_wallet",
                )
            ],
            [InlineKeyboardButton("Back", callback_data="/back_to_home_screen")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.sendPhoto(
            chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption="💰 WALLETS: Select an option",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def create_new_wallet_handler(
        user_id: int | str, update: Update, first_attempt: bool = False
    ) -> None:
        data = create_wallet_address()
        wallet_address = data.get("public_key")
        if validate_public_key(str(wallet_address)):
            wallet_id = db_manager.insert_wallet(
                data.get("public_key"), data.get("encrypted_private_key")
            )
            if wallet_id is not None:
                db_manager.insert_user(user_id, wallet_id)
                user_balance = 0
                retry_index = 0
                while retry_index < MAX_RETRIES:
                    try:
                        user_balance = solanaClient.get_balance(pubkey=Pubkey.from_string(str(wallet_address))).value
                        break
                    except Exception as e:
                        print(e, "Error in /agree")
                        await asyncio.sleep(2)
                    finally:
                        retry_index = retry_index + 1

                if first_attempt:
                    keyboard = [
                        [InlineKeyboardButton("Home Page 🏠", callback_data="/back_to_home_screen")],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update._bot.send_message(
                        chat_id=user_id,
                        text=f"""Wallet created successfully!

    Wallet: <code>{data.get('public_key')}</code>
    Balance:<code>{user_balance}</code> LAMPORTs""",
                        parse_mode="HTML",
                        reply_markup=reply_markup,
                    )
                else:
                    keyboard = [
                    [InlineKeyboardButton(
                            "Create new wallet 🆕", callback_data="/create_new_wallet")],
                    [InlineKeyboardButton(
                            f"Edit wallet - ({My_Wallet_screen_handler.mask_wallet_address(str(wallet_address))}) 📝",
                            callback_data="/edit_wallet",)],
                    [InlineKeyboardButton("Back", callback_data="/back_to_home_screen")],]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await bot.sendPhoto(
                        chat_id=update.effective_chat.id,
                        photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
                        caption=f"""Wallet created successfully 🎉

Address: <code contenteditable="true">{wallet_address}</code>

BE SURE TO COPY DOWN THIS INFORMATION NOW AS IT WILL NEVER BE SHOWN AGAIN""",
                        parse_mode="HTML",
                        reply_markup=reply_markup,)

            else:
                await update._bot.send_message(
                    chat_id=update.effective_user.id,
                    text="Failed to create wallet. Please try again.",
                )

        else:
            await update._bot.send_message(
                chat_id=update.effective_user.id,
                text="Unable to create wallet. Please try again Later.",
            )
