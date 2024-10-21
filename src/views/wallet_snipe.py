from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from json import dumps, loads
import asyncio
import datetime
from src.helpers.constants import WALLET_SNIPE_MESSAGE

# load the data from local json file
data = None


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 5


class Wallet_Snipe_screen_handeler:
    @staticmethod
    async def command_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            keyboard = Wallet_Snipe_screen_handeler.get_wallet_snipe_screen_keyboard(
                DEFAULT_PAGE
            )
            reply_markup = InlineKeyboardMarkup(keyboard)
            data = await Wallet_Snipe_screen_handeler.load_wallet_snipes()

            wallet_snipes = (
                await Wallet_Snipe_screen_handeler.get_pagination_wallets_snipes(
                    page=DEFAULT_PAGE,
                    page_size=DEFAULT_PAGE_SIZE,
                )
            )

            wallet_snipes_msg_str = "\n\n".join(
                Wallet_Snipe_screen_handeler.get_wallets_snipes_message_string(
                    wallet_snipes
                )
            )

            message = """
    <b>🏆 Wallet Snipe</b>
    {wallet_snipes_msg_str}
    """.format(
                wallet_snipes_msg_str=wallet_snipes_msg_str
            )

            await update.effective_message.edit_text(
                text=message, reply_markup=reply_markup, parse_mode="HTML"
            )
        except Exception as e:
            print(e)

    async def load_wallet_snipes():
        global data
        with open("sample_wallet_snipes.json") as file:
            data = loads(file.read())

        return data

    async def get_pagination_wallets_snipes(
        page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE
    ):
        startIndex = int((page - 1) * page_size)
        lastIndex = startIndex + page_size
        print(startIndex, lastIndex)
        return data[startIndex:lastIndex]

    def get_wallets_snipes_message_string(wallet_snipes):
        messages = []
        for wallet_snipe in wallet_snipes:
            messages.append(
                WALLET_SNIPE_MESSAGE.format(
                    maker=wallet_snipe["maker"],
                    trading_volume=int(wallet_snipe["trading_volume"]),
                    realized_profit=int(wallet_snipe["realized_profit"]),
                    last_trade_timestamp=(
                        datetime.datetime.fromtimestamp(
                            wallet_snipe["last_trade_timestamp"]
                        )
                        .date()
                        .__format__("%d/%m/%Y")
                    ),
                )
            )
        return messages

    def get_wallet_snipe_screen_keyboard(page):
        keyboard = [
            [
                InlineKeyboardButton(
                    "<<", callback_data="/wallet_snipe_prev {}".format(page - 1)
                ),
                InlineKeyboardButton("Page {} 0f 10".format(page), callback_data="/"),
                InlineKeyboardButton(
                    ">>", callback_data="/wallet_snipe_next {}".format(page + 1)
                ),
            ],
            [InlineKeyboardButton("Back", callback_data="/back_to_home_screen")],
        ]
        return keyboard

    async def handle_next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        current_page = int(query.data.split()[-1])

        keyboard = Wallet_Snipe_screen_handeler.get_wallet_snipe_screen_keyboard(
            current_page
        )

        
        reply_markup = InlineKeyboardMarkup(keyboard)
        wallet_snipes = (
            await Wallet_Snipe_screen_handeler.get_pagination_wallets_snipes(
                page=current_page,
                page_size=DEFAULT_PAGE_SIZE,
            )
        )



        wallet_snipes_msg_str = "\n\n".join(
            Wallet_Snipe_screen_handeler.get_wallets_snipes_message_string(
                wallet_snipes
            )
        )

        message = """
    <b>🏆 Wallet Snipe</b>
    {wallet_snipes_msg_str}
    """.format(
                wallet_snipes_msg_str=wallet_snipes_msg_str
            )
        await update.effective_message.edit_text(
                text=message, reply_markup=reply_markup, parse_mode="HTML"
            )

    async def handle_prev_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        current_page = int(query.data.split()[-1])

        if current_page > 0:
            keyboard = Wallet_Snipe_screen_handeler.get_wallet_snipe_screen_keyboard(
                current_page
            )
            reply_markup = InlineKeyboardMarkup(keyboard)

            wallet_snipes = (
                await Wallet_Snipe_screen_handeler.get_pagination_wallets_snipes(
                    page=current_page,
                    page_size=DEFAULT_PAGE_SIZE,
                )
            )

            wallet_snipes_msg_str = "\n\n".join(
                Wallet_Snipe_screen_handeler.get_wallets_snipes_message_string(
                    wallet_snipes
                )
            )
            message = """
        <b>🏆 Wallet Snipe</b>
        {wallet_snipes_msg_str}
        """.format(
                    wallet_snipes_msg_str=wallet_snipes_msg_str
                )
            await update.effective_message.edit_text(
                    text=message, reply_markup=reply_markup, parse_mode="HTML"
                )