from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from src.helpers.common_instances import db_manager
from src.helpers.common_instances import bot
from src.config.config import SOLSCAN_WALLET_URL
from src.helpers.constants import EDIT_WALLET_MESSAGE

class Edit_Wallet_screen_handler:
    @staticmethod
    async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            wallet_address = db_manager.get_wallet_by_telegram_id(update.effective_user.id)
            if wallet_address is None:
                raise ValueError("Wallet address is None")

            keyboard = [
                [InlineKeyboardButton("Delete 🗑️", callback_data="/delete_wallet")],
                [InlineKeyboardButton(
                    "Open in web 🌐",
                    url=SOLSCAN_WALLET_URL.format(wallet_address=wallet_address)
                )],
                [InlineKeyboardButton("Deposit 💵", callback_data="/deposit"),
                 InlineKeyboardButton("Withdraw 💸", callback_data="/withdraw")],
                [InlineKeyboardButton("Back", callback_data="/my_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_message.edit_caption(
                caption=EDIT_WALLET_MESSAGE.format(wallet_address=wallet_address),
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except AttributeError as e:
            print(f"AttributeError in command_handler: {e}")
        except ValueError as e:
            print(f"ValueError in command_handler: {e}")
        except Exception as e:
            print(f"An error occurred in Edit_Wallet_screen_handeler: {e}")
        
    @staticmethod 
    async def delete_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        wallet_address = db_manager.get_wallet_by_telegram_id(update.effective_user.id)

        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data="/yes_delete_wallet"),
            InlineKeyboardButton("❌ No", callback_data="/edit_wallet")],]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption=f"""<b>🚫 Are you sure you want to delete this wallet?</b>

<b>Wallet Address: <code>{wallet_address}</code></b>

IF YOU DID NOT STORE YOUR PRIVATE KEY OR MNEMONIC PHRASE, YOU WILL LOSE ACCESS TO THIS WALLET FOREVER""",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    @staticmethod
    async def yes_delete_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        wallet_id = db_manager.get_wallet_id_by_telegram_id(update.effective_user.id)
        db_manager.delete_wallet_by_telegram_id(update.effective_user.id, wallet_id)
        keyboard = [
                [InlineKeyboardButton("Create new wallet 🆕", callback_data="/create_new_wallet")],
                [InlineKeyboardButton("Back", callback_data="/my_wallet")],
        ]
        


        await bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption=f"""<b>✅ Wallet deleted successfully!</b>""",
            reply_markup = InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )       

    @staticmethod
    async def if_wallet_have_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        db_manager.deleted_wallet_having_balance(update.effective_user.id)
        keyboard = [
                [InlineKeyboardButton("Create new wallet 🆕", callback_data="/create_new_wallet")],
                [InlineKeyboardButton("Back", callback_data="/my_wallet")],
        ]
        


        await bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-3d-render-of-crypto-currency-and-nft-composition-image_3828737.jpg",
            caption=f"""<b>✅ Wallet deleted successfully!</b>""",
            reply_markup = InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        ) 

    @staticmethod
    async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        await update.effective_message.reply_text(
            text="""📨 Provide wallet address below

Currency : <code id="sol">SOL</code>
Chain&Protocol : <code id="spl">SOL (SPL)</code>

BE CAREFULL TO PROVIDE WALLET ADDRESS, CHECK IT TWICE
IF YOU PROVIDE WRONG WALLET ADDRESS, YOU MAY LOSE YOUR FUNDS
WE ARE NOT RESPONSIBLE FOR ANY LOSS OF FUNDS
Chain and Protocol are important, please provide them correctly""",
    parse_mode="HTML"
)