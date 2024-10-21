from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
class Positions_screen_handeler:
    @staticmethod
    async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
                [InlineKeyboardButton("Back", callback_data="/back_to_home_screen")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.edit_text(
                text="Positions 📈",
                reply_markup=reply_markup
            )