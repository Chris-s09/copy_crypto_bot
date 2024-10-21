from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from src.helpers.common_instances import db_manager
from src.config.config import SOLSCAN_WALLET_URL, MOONPAY_DEPOSIT_URL
from src.helpers.constants import DEPOSIT_MESSAGE


class Deposit_screen_handeler:
    @staticmethod
    async def command_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            user_id = update.effective_user.id
            wallet_address = db_manager.get_wallet_by_telegram_id(user_id)

            if wallet_address is None:
                raise ValueError(
                    "Wallet address not found for user_id: " + str(user_id)
                )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "Open in web 🌐",
                        url=SOLSCAN_WALLET_URL.format(wallet_address=wallet_address),
                    )
                ],
                [InlineKeyboardButton("Deposit 💵", url=MOONPAY_DEPOSIT_URL)],
                [
                    InlineKeyboardButton(
                        "Back to Home 🏠", callback_data="/back_to_home_screen"
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = DEPOSIT_MESSAGE.format(wallet_address=wallet_address)
            if update.effective_message.text:
                await update.effective_message.edit_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            else:
                await update.effective_message.edit_caption(
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )

        except ValueError as e:
            print(f"ValueError in command_handler: {e}")
        except AttributeError as e:
            print(f"AttributeError in command_handler: {e}")
        except Exception as e:
            print(f"An error occurred in Deposit_screen_handeler: {e}")
