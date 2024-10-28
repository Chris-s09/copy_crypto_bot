from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from src.helpers.common_instances import bot
class Settings_screen_handler:
    @staticmethod
    async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
                [InlineKeyboardButton("Buy Settings 💸", callback_data="/buy_settings"),
                InlineKeyboardButton("Sell Settings 🤑", callback_data="/sell_settings")],
                [InlineKeyboardButton("Back", callback_data="/back_to_home_screen")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_photo(
                
                chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption="⚙️ SETTINGS: Select an option",
            reply_markup=reply_markup
            )


    @staticmethod  
    async def buy_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
                [InlineKeyboardButton("Edit buy amount 📝", callback_data="/edit_buy_amount")],
                [InlineKeyboardButton("Edit slippage 📝", callback_data="/slippage")],
                [InlineKeyboardButton("Consecutive Buy 📝", callback_data="/consecutive_buy")],
                [InlineKeyboardButton("Back", callback_data="/settings")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_photo(
                
                chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption="⚙️ SETTINGS: Select an option",
            reply_markup=reply_markup,
            )

    @staticmethod
    async def sell_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
                [InlineKeyboardButton("Select Your Sell Type ⬇️", callback_data="/select_your_sell_type")],
                [InlineKeyboardButton("ALL", callback_data="/sell_all"),
                 InlineKeyboardButton("PERCENTAGE", callback_data="/sell_percentage")],
                [InlineKeyboardButton("Edit stop loss", callback_data="/edit_stop_loss")],
                [InlineKeyboardButton("Edit take profit", callback_data="/edit_take_profit")],
                [InlineKeyboardButton("Back", callback_data="/settings")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_photo(
                
                chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption="⚙️ SETTINGS: Select an option",
            reply_markup=reply_markup,
            )

    