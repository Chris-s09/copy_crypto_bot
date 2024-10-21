from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CallbackContext,
)
from src.views.deposit_screen import Deposit_screen_handeler
from src.views.my_wallet_screen import My_Wallet_screen_handeler
from src.views.positions_screen import Positions_screen_handeler
from src.views.referral_screen import Referral_screen_handeler
from src.views.settings_screen import Settings_screen_handeler
from src.views.wallet_snipe import Wallet_Snipe_screen_handeler
from src.views.edit_wallet_screen import Edit_Wallet_screen_handeler
from src.helpers.wallet_generator import create_wallet_address
from telegram.helpers import escape_markdown
from src.db_connection.connectionpg import DatabaseManager
from src.config.config import (
    BOT_TOKEN,
    SOLANA_URL,
    SWAP_FEES,
    ENVIRONMENT,
    SELL_PRECENTAGE,
    DEBUGGING,
)
from solana.rpc.api import Client
from src.helpers.context import UserContext
from solders.pubkey import Pubkey as PublicKey  # type: ignore
from solders.signature import Signature  # type: ignore
from base58 import b58decode
from src.helpers.constants import COPY_TRADE_MESSAGE, ALERT_MESSAGE, WSOL, GREETING_MESSAGE
import asyncio
from shedular import monitor_changes
from src.handlers.Alert_Handler import sendMessage
from src.trades_logic.jupeter_trading import get_swap_quote, execute_swap
from src.handlers.Wallet import Wallet
from src.handlers.Alert_Handler import alert_manager
from spl.token.instructions import transfer, TransferParams
from spl.token.constants import TOKEN_PROGRAM_ID
from platformFee import transfer_fee
import textwrap
from src.helpers.common_instances import solanaClient, db_manager
from src.helpers.constants import MAX_RETRIES

user_context = UserContext()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    wallet_address = db_manager.get_wallet_by_telegram_id(user_id)
    is_user_exist = db_manager.user_exists(user_id)

    if is_user_exist:
        keyboard = [
            [InlineKeyboardButton(" 🏆Wallet Snipe", callback_data=f"/wallet_snipe")],
            [
                InlineKeyboardButton(
                    "My Wallet (Total ~ 0 SOL) 💰", callback_data=f"/my_wallet"
                )
            ],
            [InlineKeyboardButton("Deposit 💵", callback_data=f"/deposit")],
            [
                InlineKeyboardButton("Positions 📈", callback_data=f"/positions"),
                InlineKeyboardButton("Copy Trading 🤖", callback_data=f"/copy_trade"),
            ],
            [
                InlineKeyboardButton("Referral 🎁", callback_data=f"/referral 🎁"),
                InlineKeyboardButton("Settings ⚙️", callback_data=f"/settings"),
            ],
            [
                InlineKeyboardButton("📢 Community Channel", url="www.google.com"),
                InlineKeyboardButton("📚 Tutorials", url="www.google.com"),
            ],
            [InlineKeyboardButton("Refresh 🔄", callback_data=f"/refresh")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        user_balance = 0
        retry_index = 0
        while retry_index < MAX_RETRIES:
            try:
                user_balance = solanaClient.get_balance(
                    PublicKey(b58decode(wallet_address))
                ).value
                break
            except Exception as e:
                print(e, "Error in start method")
                await asyncio.sleep(2)
            finally:
                retry_index = retry_index + 1

        # print(user_balance,'000000000000',type(wallet_address))
        # user_context.clear_user(user_id)

        await update._bot.send_message(
            chat_id=user_id,
            text=textwrap.dedent(
                GREETING_MESSAGE.format(
                    user_first_name=user_first_name,
                    wallet_address=wallet_address,
                    user_balance=user_balance,
                )
            ),
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        return
    else:
        keyboard = [
            [InlineKeyboardButton("Agree", callback_data="/agree")],
            [InlineKeyboardButton("Not Agree", callback_data="/not_agree")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.reply_text(
            "Do you agree to create a wallet?", reply_markup=reply_markup
        )


def validate_public_key(public_key):
    # print(type(public_key),public_key,'00000000000')
    try:
        # Assuming public_key is a Base58 encoded string, not a PublicKey object
        if isinstance(public_key, str):  # Check if the input is a string
            valid_public_key = PublicKey(b58decode(public_key))
            return True
        if isinstance(public_key, PublicKey):
            valid_public_key = public_key
            return True
    except ValueError:
        print(f"Public Key {public_key} is invalid.")
        return False


def escape_markdown_v2(text: str):
    text = str(text).replace("\\", "\\\\")
    escape_chars = "._*[]()~`>#-+=|{}!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def format_text(text: str):
    special_chars = [
        "\\",
        "_",
        "[",
        "]",
        "(",
        ")",
        "~",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    escaped_text = text.replace("\\", "\\\\")
    for char in special_chars:
        if char != "\\":
            escaped_text = escaped_text.replace(char, f"\\{char}")

    return escaped_text


def truncate_address(address, length=10):
    return address[:4] + "..." + address[-4:] if len(address) > length else address


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the callback query when a button is pressed."""
    query = update.callback_query
    query_data = query.data.split(" ", 1)
    match_query = query_data[0]
    match_query_data = query_data[1] if len(query_data) > 1 else None
    user_id = update.effective_user.id
    if DEBUGGING:
        print(match_query, " ---------------------------------", user_id)
    match match_query:
        case "/agree":
            if not db_manager.user_exists(user_id):
                await My_Wallet_screen_handeler.create_new_wallet_handler(user_id, update,first_attempt=True)
            else:
                await update._bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"You Have Already Excepted T&C.\n\n Click: /start",
                )
        case "/not_agree":

            await update._bot.send_message(
                chat_id=update.effective_user.id, text="Operation Canceled"
            )
        case "/copy_trade":
            wallet_address = db_manager.get_wallet_by_telegram_id(telegram_id=user_id)

            user_trade_data = db_manager.get_wallet_record_by_telegram_id_(user_id)

            ids = []
            target_wallet = []
            tag = []
            is_active = []
            for item in user_trade_data:
                ids.append(item[0])
                target_wallet.append(item[2])
                tag.append(item[3])
                is_active.append(item[13])

            keyboard = []
            for i in range(0, len(ids), 2):
                row = []
                for j in range(i, min(i + 2, len(ids))):  #
                    row.append(
                        InlineKeyboardButton(
                            f"{'🟢' if is_active[j] else '🟠'} {j+1}- {tag[j] if tag[j] else ''}",
                            callback_data=f"/update_copy_wallet {ids[j]}",
                        )
                    )

                keyboard.append(row)

            keyboard.extend(
                [
                    [InlineKeyboardButton("Add new copy address 🆕", callback_data="/new_wallet")],
                    [InlineKeyboardButton("Pause All", callback_data=f"/pause_all")],
                    [
                        InlineKeyboardButton(
                            "Back", callback_data="/back_to_home_screen"
                        )
                    ],
                ]
            )

            reply_markup = InlineKeyboardMarkup(keyboard)

            message_content = COPY_TRADE_MESSAGE.format(wallet_address)
            escaped_wallets = [(wallet) for wallet in target_wallet]
            tags_and_wallets = "\n".join(
                [
                    f"{'🟢' if is_active[j] else '🟠'} {tag if tag else '' } - {truncate_address(target_wallet)}"
                    for tag, target_wallet in zip(tag, escaped_wallets)
                ]
            )

            escaped_message_content = escape_markdown_v2(message_content)
            escaped_tags_and_wallets = escape_markdown_v2(tags_and_wallets)
            full_message_content = escaped_message_content + escaped_tags_and_wallets

            await update.effective_message.edit_text(
                text=f"{full_message_content}",
                reply_markup=reply_markup,
                parse_mode="MarkdownV2",
            )
        case "/update_copy_wallet":

            user_trade_data = (
                db_manager.get_wallet_records_with_column_names_for_telegram_id(
                    user_id, id=match_query_data
                )
            )

            target_wallet_text = user_trade_data[0][0].get("target_wallet")

            tag_text = user_trade_data[0][0].get("tag")

            buy_percentage_text = user_trade_data[0][0].get("buy_percentage")

            copy_sell_str = user_trade_data[0][0].get("copy_sell")

            buy_gas_text = user_trade_data[0][0].get("buy_gas")

            sell_gas_text = user_trade_data[0][0].get("sell_gas")

            slippage_text = user_trade_data[0][0].get("slippage")

            is_active_text = user_trade_data[0][0].get("is_active")

            id = user_trade_data[0][0].get("id")

            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {truncate_address(target_wallet_text)}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Percentage: {buy_percentage_text}",
                        callback_data="/buy_percentage",
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_str}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text}%", callback_data="/slippage"
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [
                    InlineKeyboardButton(
                        f"Is Active {is_active_text}", callback_data="/is_active"
                    ),
                    InlineKeyboardButton(
                        "Delete", callback_data=f"/delete_copy_wallet {id}"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.effective_message.edit_text(
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade.
                                                                           
To manage your Copy Trade:
            - Click the “Active” button to “Pause” the Copy Trade.
            - Delete a Copy Trade by clicking the “Delete” button.
            """
                ),
                reply_markup=reply_markup,
            )
        case "/new_wallet":

            user_trade_data = user_context.get_all(user_id)

            target_wallet_text = (
                user_trade_data.get("target_wallet")
                if user_trade_data.get("target_wallet")
                else f"-"
            )

            tag_text = (
                user_trade_data.get("tag") if user_trade_data.get("tag") else f"-"
            )

            buy_percentage_text = (
                user_trade_data.get("buy_percentage_text")
                if user_trade_data.get("buy_percentage_text")
                else f""
            )

            copy_sell_str = user_trade_data.get("copy_sell_bool")
            if copy_sell_str == "True":
                copy_sell_bool = True
            elif copy_sell_str == "False":
                copy_sell_bool = False
            else:
                copy_sell_bool = True
                user_context.set(user_id, "copy_sell_bool", str(copy_sell_bool))

            buy_gas_text = (
                user_trade_data.get("buy_gas")
                if user_trade_data.get("buy_gas")
                else f""
            )

            sell_gas_text = (
                user_trade_data.get("sell_gas")
                if user_trade_data.get("sell_gas")
                else f""
            )

            slippage_text = (
                user_trade_data.get("slippage")
                if user_trade_data.get("slippage")
                else f""
            )

            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {truncate_address(target_wallet_text)}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Percentage: {buy_percentage_text}",
                        callback_data="/buy_percentage",
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.effective_message.edit_text(
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )
        case "/target_wallet":
            if not user_context.get(user_id, "target_wallet_check"):
                user_context.set(user_id, "target_wallet_check", True)
                await update._bot.send_message(
                    chat_id=user_id,
                    text="Enter the target wallet address to copy trade",
                )
            else:

                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )

            return
        case "/tag":
            if not user_context.get(user_id, "tag_check"):
                user_context.set(user_id, "tag_check", True)
                await update._bot.send_message(
                    chat_id=user_id,
                    text="Enter a custom name for this copy trade setup",
                )
            else:
                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )
            return
        case "/buy_percentage":
            if not user_context.get(user_id, "buy_percentage_check"):
                user_context.set(user_id, "buy_percentage_check", True)
                await update._bot.send_message(
                    chat_id=user_id,
                    text="Enter the percentage of the target's buy amount to copy trade with. E.g. with 50%, if the target buys with 1 SOL, you will buy with 0.5 SOL. If you want to buy with a fixed sol amount instead, enter a number. E.g. 0.1 SOL will buy with 0.1 SOL regardless of the target's buy amount.",
                )
            else:
                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )
            return
        case "/copy_sells":
            target_wallet_text = (
                user_context.get(user_id, "target_wallet")
                if user_context.get(user_id, "target_wallet")
                else f"-"
            )

            tag_text = (
                user_context.get(user_id, "tag")
                if user_context.get(user_id, "tag")
                else f"-"
            )

            # buy_percentage_text = 'Buy Percentage: ' + user_context.get(user_id, 'buy_percentage') if '%' in user_context.get(user_id, 'buy_percentage') else ('' if user_context.get(user_id,'buy_percentage') is None else 'Sol Amount: '+ str(user_context.get(user_id,'buy_percentage') + ' SOL'))
            buy_percentage_text = (
                "Sol Amount: "
                if user_context.get(user_id, "buy_percentage") is not None
                and "%" not in user_context.get(user_id, "buy_percentage")
                else "Buy Percentage:"
            ) + (
                ""
                if user_context.get(user_id, "buy_percentage") is None
                else (
                    user_context.get(user_id, "buy_percentage")
                    if "%" in user_context.get(user_id, "buy_percentage")
                    else str(user_context.get(user_id, "buy_percentage") + " SOL")
                )
            )

            copy_sell_str = user_context.get(user_id, "copy_sell_bool")
            if copy_sell_str == "True":
                copy_sell_bool = False
                user_context.set(user_id, "copy_sell_bool", str(copy_sell_bool))
            elif copy_sell_str == "False":
                copy_sell_bool = True
                user_context.set(user_id, "copy_sell_bool", str(copy_sell_bool))
            else:
                copy_sell_bool = True
                user_context.set(user_id, "copy_sell_bool", str(copy_sell_bool))

            buy_gas_text = (
                user_context.get(user_id, "buy_gas")
                if user_context.get(user_id, "buy_gas")
                else f""
            )

            sell_gas_text = (
                user_context.get(user_id, "sell_gas")
                if user_context.get(user_id, "sell_gas")
                else f""
            )

            slippage_text = (
                user_context.get(user_id, "slippage")
                if user_context.get(user_id, "slippage")
                else f""
            )
            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {target_wallet_text}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{buy_percentage_text}", callback_data="/buy_percentage"
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.effective_message.edit_text(
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )

            return
        case "/buy_gas":
            if not user_context.get(user_id, "buy_gas_check"):
                user_context.set(user_id, "buy_gas_check", True)
                await update._bot.send_message(
                    chat_id=user_id,
                    text="Enter the priority fee to pay for buy trades. E.g 0.01 for 0.01 SOL",
                )
            else:
                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )

            return
        case "/sell_gas":
            if not user_context.get(user_id, "sell_gas_check"):
                user_context.set(user_id, "sell_gas_check", True)
                await update._bot.send_message(
                    chat_id=user_id,
                    text="Enter the priority fee to pay for buy trades. E.g 0.01 for 0.01 SOL",
                )
            else:
                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )

            return
        case "/slippage":
            if not user_context.get(user_id, "slippage_check"):
                user_context.set(user_id, "slippage_check", True)
                await update._bot.send_message(
                    chat_id=user_id, text="Enter slippage % to use on copy trades"
                )
            else:
                await update._bot.send_message(
                    chat_id=user_id,
                    text="You have already initiated this action. Please wait for further instructions.",
                )

            return
        case "/add":
            try:
                user_id = update.effective_user.id
                target_wallet = user_context.get(user_id, "target_wallet")
                tag = user_context.get(user_id, "tag")
                buy_percentage = (
                    user_context.get(user_id, "buy_percentage")
                    if "%" not in user_context.get(user_id, "buy_percentage")
                    else user_context.get(user_id, "buy_percentage")[:-1]
                )
                copy_sell_bool = user_context.get(user_id, "copy_sell_bool")
                buy_gas = user_context.get(user_id, "buy_gas")
                slippage = (
                    user_context.get(user_id, "slippage")
                    if "%" not in user_context.get(user_id, "slippage")
                    else user_context.get(user_id, "slippage")[:-1]
                )
                sell_gas = user_context.get(user_id, "sell_gas")
                is_user_exist = db_manager.user_exists(user_id)
                print(target_wallet)
                if target_wallet:
                    db_manager.add_all_trade_data(
                        user_id,
                        target_wallet,
                        tag,
                        buy_percentage,
                        copy_sell_bool,
                        sell_gas,
                        slippage,
                        buy_gas,
                    )
                    wallet_address = db_manager.get_wallet_by_telegram_id(
                        telegram_id=user_id
                    )

                    user_trade_data = db_manager.get_wallet_record_by_telegram_id_(
                        user_id
                    )

                    ids = []
                    target_wallet = []
                    tag = []
                    is_active = []
                    for item in user_trade_data:
                        ids.append(item[0])
                        target_wallet.append(item[2])
                        tag.append(item[3])
                        is_active.append(item[13])

                    keyboard = []
                    for i in range(0, len(ids), 2):
                        row = []
                        for j in range(i, min(i + 2, len(ids))):  #
                            row.append(
                                InlineKeyboardButton(
                                    f"{'🟢' if is_active[j] else '🟠'} {j+1}- {tag[j]}",
                                    callback_data=f"/update_copy_wallet {ids[j]}",
                                )
                            )

                        keyboard.append(row)

                    keyboard.extend(
                        [
                            [InlineKeyboardButton("New", callback_data="/new_wallet")],
                            [
                                InlineKeyboardButton(
                                    "Pause All", callback_data=f"/pause_all"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Back", callback_data="/back_to_home_screen"
                                )
                            ],
                        ]
                    )

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    message_content = COPY_TRADE_MESSAGE.format(wallet_address)
                    escaped_wallets = [(wallet) for wallet in target_wallet]
                    tags_and_wallets = "\n".join(
                        [
                            f"{'🟢' if is_active[j] else '🟠'} {tag} - {truncate_address(target_wallet)}"
                            for tag, target_wallet in zip(tag, escaped_wallets)
                        ]
                    )

                    escaped_message_content = escape_markdown_v2(message_content)
                    escaped_tags_and_wallets = escape_markdown_v2(tags_and_wallets)
                    full_message_content = (
                        escaped_message_content + escaped_tags_and_wallets
                    )

                    user_context.clear_user(user_id)
                    await update.effective_message.edit_text(
                        text=f"{full_message_content}",
                        reply_markup=reply_markup,
                        parse_mode="MarkdownV2",
                    )
                else:
                    await update.effective_message.reply_text(
                        f"Cannot add trade without target wallet{data}"
                    )
            except Exception as e:
                print(e, "Error in /add")
                await update.effective_message.reply_text(
                    f"Please Provide Trade Details."
                )

            data = user_context.get_all(user_id)
        case "/delete_copy_wallet":
            try:
                user_id = update.effective_user.id
                id = match_query_data

                if id:
                    db_manager.delete_all_monitor_wallets_data(user_id, id)
                    wallet_address = db_manager.get_wallet_by_telegram_id(
                        telegram_id=user_id
                    )

                    user_trade_data = db_manager.get_wallet_record_by_telegram_id_(
                        user_id
                    )

                    ids = []
                    target_wallet = []
                    tag = []
                    is_active = []
                    for item in user_trade_data:
                        ids.append(item[0])
                        target_wallet.append(item[2])
                        tag.append(item[3])
                        is_active.append(item[13])

                    keyboard = []
                    for i in range(0, len(ids), 2):
                        row = []
                        for j in range(i, min(i + 2, len(ids))):  #
                            row.append(
                                InlineKeyboardButton(
                                    f"{'🟢' if is_active[j] else '🟠'} {j+1}- {tag[j]}",
                                    callback_data=f"/update_copy_wallet {ids[j]}",
                                )
                            )

                        keyboard.append(row)

                    keyboard.extend(
                        [
                            [InlineKeyboardButton("New", callback_data="/new_wallet")],
                            [
                                InlineKeyboardButton(
                                    "Pause All", callback_data=f"/pause_all"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Back", callback_data="/back_to_home_screen"
                                )
                            ],
                        ]
                    )

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    message_content = COPY_TRADE_MESSAGE.format(wallet_address)
                    escaped_wallets = [(wallet) for wallet in target_wallet]
                    tags_and_wallets = "\n".join(
                        [
                            f"{'🟢' if is_active[j] else '🟠'} {tag} - {truncate_address(target_wallet)}"
                            for tag, target_wallet in zip(tag, escaped_wallets)
                        ]
                    )

                    escaped_message_content = escape_markdown_v2(message_content)
                    escaped_tags_and_wallets = escape_markdown_v2(tags_and_wallets)
                    full_message_content = (
                        escaped_message_content + escaped_tags_and_wallets
                    )

                    await update.effective_message.edit_text(
                        text=f"{full_message_content}",
                        reply_markup=reply_markup,
                        parse_mode="MarkdownV2",
                    )
                else:
                    await update.effective_message.reply_text(f"Trade does not exists")
            except Exception as e:
                await update.effective_message.reply_text(
                    f"Unable to delete pelease Try again or Refresh by clicking /start."
                )

            data = user_context.get_all(user_id)
        case "/back_to_home_screen":
            await start(update, context)
        case "/execute_swap":
            # try:
            user_id = update.effective_user.id
            alert_id = match_query_data
            # print(alert_id,'00000000000')

            alert_data = alert_manager.get(alert_id)
            if not alert_data:
                await update.effective_message.reply_text("Something went wrong")
                print("Alert not found with ID", alert_id)
                return

            wallet_address, change_type, token, telegram_id = (
                alert_data.get("wallet_address"),
                alert_data.get("change_type"),
                alert_data.get("token"),
                alert_data.get("telegram_id"),
            )

            user_wallet_info = Wallet.get_wallet_info_by_tgid(user_id)
            target_wallet_config = db_manager.get_monitor_wallet_by_telegram_id_token(
                user_id, wallet_address
            )
            token_balance_in_users_wallet_info = (
                Wallet.get_token_balance_data_in_wallet(
                    wallet_address=user_wallet_info.get("wallet_address"),
                    token_address=token,
                )
            )

            # print(token_balance_in_users_wallet_info,'token_balance_in_users_wallet_info--------------')
            token_balance_in_users_wallet = 0
            if token_balance_in_users_wallet_info:
                token_balance_in_users_wallet = token_balance_in_users_wallet_info.get(
                    "balance"
                )

            sol_token_price_info = Wallet.get_token_price(
                "So11111111111111111111111111111111111111112"
            )
            target_wallet_buy_percentage = (
                target_wallet_config[0][0]["buy_percentage"] / 100
            )

            target_wallet_sell_percentage = SELL_PRECENTAGE
            token_overview = Wallet.get_token_overview(token)
            token_name = token_overview.get("name")
            token_symbol = token_overview.get("symbol")
            token_mc = token_overview.get("mc")

            BUY = change_type == "BUY"
            SELL = change_type == "SELL"

            if BUY:
                amount = target_wallet_buy_percentage * user_wallet_info.get("balance")
                if amount < 10000:
                    await sendMessage(
                        tgId=user_id,
                        text="Not Enough SOL balance add atleast 0\.0001 Sol",
                    )
                    return

            if SELL:
                amount = target_wallet_sell_percentage * token_balance_in_users_wallet

                if amount <= 0:
                    await sendMessage(
                        tgId=user_id, text="Not Enough Token balance in wallet"
                    )
                    return

            if ENVIRONMENT == "dev" and False:
                amount = 10000

            # if amount < 10000:
            #     await sendMessage(tgId=user_id,text='Not Enough SOL balance add atleast 0\.0001 Sol')
            #     return

            swap_quote_data = {}
            try:
                swap_quote_data = await get_swap_quote(
                    input_mint=WSOL if BUY else token,
                    output_mint=WSOL if SELL else token,
                    amount_in_lamports=amount,
                    telegram_id=user_id,
                )
            except Exception as e:
                print("Error in swap_quote :", e)
                await update.effective_message.edit_text(f" Cannot find any route")
                return

            swap_fee = SWAP_FEES * 100

            if swap_quote_data is None:
                await update.effective_message.edit_text(f" Cannot find any route")
                return

            in_ammount = swap_quote_data.get("inAmount")
            out_ammount = swap_quote_data.get("outAmount")

            keyboard = [
                [
                    InlineKeyboardButton(
                        "Confirm", callback_data=f"/confirm_swaping {alert_id}"
                    )
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_message.edit_text(
                f" Token Address: {token}\n\n Token Name: {token_name}\n\n Token Symbol: {token_symbol}\n\n MC: ${round(token_mc, 2)}\n\n In amount: {in_ammount}\n\n Out amount: {out_ammount}\n\n Platform Fee: {round(swap_fee)}%",
                reply_markup=reply_markup,
            )
        # except Exception as e:
        #     print("Error in /execute_swap:",e)
        case "/confirm_swaping":
            # try:
            user_id = update.effective_user.id
            alert_id = match_query_data
            print(alert_id, "alert_id confirm part--------")
            alert_data = alert_manager.get(alert_id)
            wallet_address, change_type, token, telegram_id = (
                alert_data.get("wallet_address"),
                alert_data.get("change_type"),
                alert_data.get("token"),
                alert_data.get("telegram_id"),
            )

            user_wallet_info = Wallet.get_wallet_info_by_tgid(user_id)
            # print(user_wallet_info,'user_wallet_info-------------------')
            target_wallet_config = db_manager.get_monitor_wallet_by_telegram_id_token(
                user_id, wallet_address
            )
            token_balance_in_users_wallet_info = (
                Wallet.get_token_balance_data_in_wallet(
                    wallet_address=user_wallet_info.get("wallet_address"),
                    token_address=token,
                )
            )

            sol_token_price_info = Wallet.get_token_price(
                "So11111111111111111111111111111111111111112"
            )
            target_wallet_buy_percentage = (
                target_wallet_config[0][0]["buy_percentage"] / 100
            )
            target_wallet_sell_percentage = SELL_PRECENTAGE

            BUY = change_type == "BUY"
            SELL = change_type == "SELL"

            if BUY:
                amount = float(target_wallet_buy_percentage) * user_wallet_info.get(
                    "balance"
                )
                print(amount, "buyed44444444444444444444444444444")

            if SELL:
                amount = (
                    (
                        target_wallet_sell_percentage
                        * token_balance_in_users_wallet_info.get("balance")
                    )
                    if token_balance_in_users_wallet_info
                    else 0
                )
                print(
                    amount,
                    token_balance_in_users_wallet_info,
                    token,
                    wallet_address,
                    "selled333333333333333333333333333333333333333333",
                )

            if ENVIRONMENT == "dev" and False:
                amount = 10000

            # if amount < 10000:
            #     await sendMessage(tgId=user_id,text='Not Enough SOL balance add atleast 0\.0001 Sol')
            #     return

            swap_fee = amount * SWAP_FEES
            sol_token_price = sol_token_price_info.get("value")
            token_balance_in_user_wallet_usd = (
                token_balance_in_users_wallet_info.get("valueUsd")
                if token_balance_in_users_wallet_info
                else 0
            )
            token_balance_in_users_wallet = (
                token_balance_in_users_wallet_info.get("balance")
                if token_balance_in_users_wallet_info
                else 0
            )

            if SELL:
                if (
                    sol_token_price is not None
                    and token_balance_in_user_wallet_usd is not None
                ):
                    swap_fee = (
                        sol_token_price / token_balance_in_user_wallet_usd * SWAP_FEES
                    )
                    print(
                        swap_fee,
                        sol_token_price,
                        token_balance_in_user_wallet_usd,
                        "sell_swap_fee_tokne_price_token_balnace_usd88888888888888888888888888888",
                    )
                else:
                    await sendMessage(
                        tgId=user_id, text="Not Enough Token Balance In wallet"
                    )
                    return

            # amount = 10000 #hardcoded
            total_amount = swap_fee + amount

            if total_amount:
                if BUY:
                    if total_amount > (user_wallet_info.get("balance")):
                        await sendMessage(
                            tgId=user_id,
                            text="Not Enough Sol balance for Platform Fee:",
                        )
                        return
                if SELL:
                    if amount > (token_balance_in_users_wallet) and swap_fee > (
                        user_wallet_info.get("balance")
                    ):
                        await sendMessage(
                            tgId=user_id,
                            text="Not Enough Token balance or SOL balance for Platform Fee:",
                        )
                        return

                # (user_wallet_info.get('balance') if BUY else token_balance_in_users_wallet)
                # # 2999.5 10000 59990000
                # # print(swap_fee,amount,user_wallet_info.get('balance'))
                # print(swap_fee,amount,token_balance_in_users_wallet)
                # await sendMessage(tgId=user_id,text='Not Enough amount to process:')
                # return

                try:
                    tx_id, message = await execute_swap(
                        input_mint=WSOL if BUY else token,
                        output_mint=WSOL if SELL else token,
                        amount_in_lamports=amount,
                        telegram_id=telegram_id,
                    )
                    print(tx_id, "==============================================")
                    await asyncio.sleep(5)
                    if tx_id:
                        await transfer_fee(
                            transfer_fee=int(amount * SWAP_FEES),
                            telegram_id=user_id,
                            # telegram_id=1484746944,
                        )
                        print(
                            tx_id,
                            "if  tx_id||||||||||||||||||||||||||||||||||||||||||||||||",
                        )

                        await update._bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"Trade executed successfully \n Tx: {tx_id}",
                        )
                    else:
                        await update._bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"Trade Failed. \n\n{message}",
                        )
                except Exception as e:
                    print("Error in execute_swap in /confirm_swaping :", e)
                    await update._bot.send_message(
                        chat_id=update.effective_chat.id, text=f"Trade Failed.{e}"
                    )
        # except Exception as e:
        #     print("Error in /confirm_swaping:",e)
        case "/wallet_snipe":
            try:
                await Wallet_Snipe_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /wallet_snipe:", e)

        case "/my_wallet":
            try:
                await My_Wallet_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in my_wallet:", e)

        case "/deposit":
            try:
                await Deposit_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /deposit:", e)

        case "/positions":
            try:
                await Positions_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /positions:", e)
        case "/referral":
            try:
                await Referral_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /referral:", e)
        case "/settings":
            try:
                await Settings_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /settings:", e)
        case "/refresh":
            await start(update, context)
        case "/wallet_snipe_prev":
            try:
                await Wallet_Snipe_screen_handeler.handle_prev_command(update, context)
            except Exception as e:    
                print("Error in /wallet_snipe_prev:", e)
        case "/wallet_snipe_next":
            try:
                await Wallet_Snipe_screen_handeler.handle_next_command(update, context)
            except Exception as e:
                print("Error in /wallet_snipe_next:", e)
        case "/edit_wallet":
            try:
                await Edit_Wallet_screen_handeler.command_handler(update, context)
            except Exception as e:
                print("Error in /edit_wallet:", e)
        case "/create_new_wallet":
            try:
                if not db_manager.user_exists(user_id):
                    await My_Wallet_screen_handeler.create_new_wallet_handler(user_id, update)
                else:
                    await update._bot.send_message(
                    chat_id=update.effective_user.id,
                    text="🚫Maximum of 1 wallets defined, delete or replace an existing one",
                )
            except Exception as e:
                print("Error in /create_new_wallet:", e)
        case "/delete_wallet":
            try:
                await Edit_Wallet_screen_handeler.delete_wallet_handler(update, context)
            except Exception as e:
                print("Error in /delete_wallet:", e)
        case "/yes_delete_wallet":
            wallet_address = db_manager.get_wallet_by_telegram_id(user_id)

            user_balance = solanaClient.get_balance(PublicKey.from_string(wallet_address)).value
            print(user_balance,"-----------------")

            print(user_balance,"-----------------")
            try:
                if user_balance > 0:
                    await Edit_Wallet_screen_handeler.if_wallet_have_balance_handler(update, context)
                else:
                    await Edit_Wallet_screen_handeler.yes_delete_wallet_handler(update, context)
            except Exception as e:
                print("Error in /yes_delete_wallet:", e)
        case "/withdraw":
            try:
                await Edit_Wallet_screen_handeler.withdraw_handler(update, context)
            except Exception as e:
                print("Error in /withdraw:", e)
        case "/buy_settings":
            try:
                await Settings_screen_handeler.buy_settings(update, context)
            except Exception as e:
                print("Error in /buy_settings:", e)
        case "/sell_settings":
            try:
                await Settings_screen_handeler.sell_settings(update, context)
            except Exception as e:
                print("Error in /sell_settings:", e)
        case _:
            await start(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if target_wallet_check := user_context.get(user_id, "target_wallet_check"):
        if validate_public_key(text):
            if text != db_manager.get_wallet_by_telegram_id(user_id):
                target_wallet = text
                # db_manager.add_update_target_wallet(user_id, target_wallet)
                user_context.set(user_id, "target_wallet", target_wallet)
                user_context.clear(user_id, "target_wallet_check")

                tag_text = (
                    user_context.get(user_id, "tag")
                    if user_context.get(user_id, "tag")
                    else "-"
                )
                target_wallet_text = (
                    user_context.get(user_id, "target_wallet")
                    if user_context.get(user_id, "target_wallet")
                    else "-"
                )
                buy_percentage_text = (
                    user_context.get(user_id, "buy_percentage")
                    if user_context.get(user_id, "buy_percentage")
                    else ""
                )
                buy_gas_text = (
                    user_context.get(user_id, "buy_gas")
                    if user_context.get(user_id, "buy_gas")
                    else ""
                )
                copy_sell_bool = (
                    user_context.get(user_id, "copy_sell_bool")
                    if user_context.get(user_id, "copy_sell_bool")
                    else ""
                )
                slippage_text = (
                    user_context.get(user_id, "slippage")
                    if user_context.get(user_id, "slippage")
                    else ""
                )
                sell_gas_text = (
                    user_context.get(user_id, "sell_gas")
                    if user_context.get(user_id, "sell_gas")
                    else ""
                )
                keyboard = [
                    [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                    [
                        InlineKeyboardButton(
                            f"Target Wallet: {truncate_address(target_wallet_text)} ",
                            callback_data="/target_wallet",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"Buy Percentage: {buy_percentage_text}",
                            callback_data="/buy_percentage",
                        ),
                        InlineKeyboardButton(
                            f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                        ),
                        InlineKeyboardButton(
                            f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                            callback_data="/slippage",
                        )
                    ],
                    # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                    [InlineKeyboardButton("Add", callback_data="/add")],
                    [InlineKeyboardButton("Back", callback_data="/copy_trade")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update._bot.send_message(
                    chat_id=user_id,
                    text=escape_markdown(
                        """To setup a new Copy Trade:
                - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
                - Enter the target wallet address to copy trade.
                - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
                - Toggle on Copy Sells to copy the sells of the target wallet.
                - Click “Add” to create and activate the Copy Trade. """
                    ),
                    reply_markup=reply_markup,
                )
            else:
                user_context.set(user_id, "target_wallet_check", False)

                keyboard = [
                    [InlineKeyboardButton(f"Retry", callback_data="/target_wallet")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    text=f"You cannot copy trade to your own wallet.",
                    reply_markup=reply_markup,
                )
        else:
            user_context.set(user_id, "target_wallet_check", False)
            keyboard = [
                [InlineKeyboardButton(f"Retry", callback_data="/target_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f"Invalid address length. Make sure to send a Solana wallet.",
                reply_markup=reply_markup,
            )
    elif tag_check := user_context.get(user_id, "tag_check"):

        tag = text
        user_context.set(user_id, "tag", tag)
        user_context.clear(user_id, "tag_check")

        tag_text = (
            user_context.get(user_id, "tag")
            if user_context.get(user_id, "tag")
            else "-"
        )
        target_wallet_text = (
            user_context.get(user_id, "target_wallet")
            if user_context.get(user_id, "target_wallet")
            else "-"
        )
        buy_percentage_text = (
            user_context.get(user_id, "buy_percentage")
            if user_context.get(user_id, "buy_percentage")
            else ""
        )
        buy_gas_text = (
            user_context.get(user_id, "buy_gas")
            if user_context.get(user_id, "buy_gas")
            else ""
        )
        copy_sell_bool = (
            user_context.get(user_id, "copy_sell_bool")
            if user_context.get(user_id, "copy_sell_bool")
            else ""
        )
        slippage_text = (
            user_context.get(user_id, "slippage")
            if user_context.get(user_id, "slippage")
            else ""
        )
        sell_gas_text = (
            user_context.get(user_id, "sell_gas")
            if user_context.get(user_id, "sell_gas")
            else ""
        )
        keyboard = [
            [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
            [
                InlineKeyboardButton(
                    f"Target Wallet: {target_wallet_text}",
                    callback_data="/target_wallet",
                )
            ],
            [
                InlineKeyboardButton(
                    f"Buy Percentage: {buy_percentage_text}",
                    callback_data="/buy_percentage",
                ),
                InlineKeyboardButton(
                    f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                ),
                InlineKeyboardButton(
                    f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                    callback_data="/slippage",
                )
            ],
            # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
            [InlineKeyboardButton("Add", callback_data="/add")],
            [InlineKeyboardButton("Back", callback_data="/copy_trade")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update._bot.send_message(
            chat_id=user_id,
            text=escape_markdown(
                """To setup a new Copy Trade:
        - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
        - Enter the target wallet address to copy trade.
        - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
        - Toggle on Copy Sells to copy the sells of the target wallet.
        - Click “Add” to create and activate the Copy Trade. """
            ),
            reply_markup=reply_markup,
        )
    elif buy_percentage_check := user_context.get(user_id, "buy_percentage_check"):
        text = update.message.text
        buy_percentage, is_valid_buypercentage = process_buy_and_slippage_percentage(
            text
        )

        if is_valid_buypercentage:
            user_context.set(user_id, "buy_percentage", buy_percentage)
            user_context.clear(user_id, "buy_percentage_check")

            tag_text = (
                user_context.get(user_id, "tag")
                if user_context.get(user_id, "tag")
                else "-"
            )
            target_wallet_text = (
                user_context.get(user_id, "target_wallet")
                if user_context.get(user_id, "target_wallet")
                else "-"
            )
            buy_percentage_text = (
                "Buy Percentage: " + user_context.get(user_id, "buy_percentage")
                if "%" in user_context.get(user_id, "buy_percentage")
                else "Sol Amount: "
                + str(user_context.get(user_id, "buy_percentage") + " SOL")
            )
            buy_gas_text = (
                user_context.get(user_id, "buy_gas")
                if user_context.get(user_id, "buy_gas")
                else ""
            )
            copy_sell_bool = (
                user_context.get(user_id, "copy_sell_bool")
                if user_context.get(user_id, "copy_sell_bool")
                else ""
            )
            slippage_text = (
                user_context.get(user_id, "slippage")
                if user_context.get(user_id, "slippage")
                else ""
            )
            sell_gas_text = (
                user_context.get(user_id, "sell_gas")
                if user_context.get(user_id, "sell_gas")
                else ""
            )
            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {target_wallet_text}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{buy_percentage_text}", callback_data="/buy_percentage"
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update._bot.send_message(
                chat_id=user_id,
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )
        else:
            user_context.set(user_id, "buy_percentage_check", False)
            keyboard = [
                [InlineKeyboardButton(f"Retry", callback_data="/buy_percentage")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f"Invalid Buy Amount. Send a number greater than 0.0001. E.g. 0.5",
                reply_markup=reply_markup,
            )
    elif buy_gas_check := user_context.get(user_id, "buy_gas_check"):
        text = update.message.text
        buy_gas, is_valid_buygas = process_buy_and_sell(text)
        if is_valid_buygas:
            user_context.set(user_id, "buy_gas", buy_gas)
            user_context.clear(user_id, "buy_gas_check")

            tag_text = (
                user_context.get(user_id, "tag")
                if user_context.get(user_id, "tag")
                else "-"
            )
            target_wallet_text = (
                user_context.get(user_id, "target_wallet")
                if user_context.get(user_id, "target_wallet")
                else "-"
            )
            buy_percentage_text = (
                user_context.get(user_id, "buy_percentage")
                if user_context.get(user_id, "buy_percentage")
                else ""
            )
            buy_gas_text = (
                user_context.get(user_id, "buy_gas")
                if user_context.get(user_id, "buy_gas")
                else ""
            )
            copy_sell_bool = (
                user_context.get(user_id, "copy_sell_bool")
                if user_context.get(user_id, "copy_sell_bool")
                else ""
            )
            slippage_text = (
                user_context.get(user_id, "slippage")
                if user_context.get(user_id, "slippage")
                else ""
            )
            sell_gas_text = (
                user_context.get(user_id, "sell_gas")
                if user_context.get(user_id, "sell_gas")
                else ""
            )
            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {target_wallet_text}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Percentage: {buy_percentage_text}",
                        callback_data="/buy_percentage",
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update._bot.send_message(
                chat_id=user_id,
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )
        else:
            user_context.set(user_id, "buy_percentage_check", False)
            keyboard = [[InlineKeyboardButton(f"Retry", callback_data="/buy_gas")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f"Invalid Priority Fee. Make sure to send a number.",
                reply_markup=reply_markup,
            )
    elif sell_gas_check := user_context.get(user_id, "sell_gas_check"):
        text = update.message.text
        sell_gas, is_valid_sell_gas = process_buy_and_sell(text)

        if is_valid_sell_gas:
            user_context.set(user_id, "sell_gas", sell_gas)
            user_context.clear(user_id, "sell_gas_check")

            tag_text = (
                user_context.get(user_id, "tag")
                if user_context.get(user_id, "tag")
                else "-"
            )
            target_wallet_text = (
                user_context.get(user_id, "target_wallet")
                if user_context.get(user_id, "target_wallet")
                else "-"
            )
            buy_percentage_text = (
                user_context.get(user_id, "buy_percentage")
                if user_context.get(user_id, "buy_percentage")
                else ""
            )
            buy_gas_text = (
                user_context.get(user_id, "buy_gas")
                if user_context.get(user_id, "buy_gas")
                else ""
            )
            copy_sell_bool = (
                user_context.get(user_id, "copy_sell_bool")
                if user_context.get(user_id, "copy_sell_bool")
                else ""
            )
            slippage_text = (
                user_context.get(user_id, "slippage")
                if user_context.get(user_id, "slippage")
                else ""
            )
            sell_gas_text = (
                user_context.get(user_id, "sell_gas")
                if user_context.get(user_id, "sell_gas")
                else ""
            )
            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {target_wallet_text}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Percentage: {buy_percentage_text}",
                        callback_data="/buy_percentage",
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update._bot.send_message(
                chat_id=user_id,
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )
        else:
            user_context.set(user_id, "sell_gas_check", False)
            keyboard = [[InlineKeyboardButton(f"Retry", callback_data="/sell_gas")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f"Invalid Priority Fee. Make sure to send a number.",
                reply_markup=reply_markup,
            )
    elif slippage_check := user_context.get(user_id, "slippage_check"):
        text = update.message.text
        slippage, is_valid_slippage = process_buy_and_slippage_percentage(text)

        if is_valid_slippage:
            user_context.set(user_id, "slippage", slippage)
            user_context.clear(user_id, "slippage_check")

            tag_text = (
                user_context.get(user_id, "tag")
                if user_context.get(user_id, "tag")
                else "-"
            )
            target_wallet_text = (
                user_context.get(user_id, "target_wallet")
                if user_context.get(user_id, "target_wallet")
                else "-"
            )
            buy_percentage_text = (
                user_context.get(user_id, "buy_percentage")
                if user_context.get(user_id, "buy_percentage")
                else ""
            )
            buy_gas_text = (
                user_context.get(user_id, "buy_gas")
                if user_context.get(user_id, "buy_gas")
                else ""
            )
            copy_sell_bool = (
                user_context.get(user_id, "copy_sell_bool")
                if user_context.get(user_id, "copy_sell_bool")
                else ""
            )
            slippage_text = (
                user_context.get(user_id, "slippage")
                if user_context.get(user_id, "slippage")
                else "" if "%" in user_context.get(user_id, "slippage") else ""
            )
            sell_gas_text = (
                user_context.get(user_id, "sell_gas")
                if user_context.get(user_id, "sell_gas")
                else ""
            )
            keyboard = [
                [InlineKeyboardButton(f"Tag: {tag_text}", callback_data="/tag")],
                [
                    InlineKeyboardButton(
                        f"Target Wallet: {target_wallet_text}",
                        callback_data="/target_wallet",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Percentage: {buy_percentage_text}",
                        callback_data="/buy_percentage",
                    ),
                    InlineKeyboardButton(
                        f"Copy Sells: {copy_sell_bool}", callback_data="/copy_sells"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Buy Gas: {buy_gas_text}:", callback_data="/buy_gas"
                    ),
                    InlineKeyboardButton(
                        f"Sell Gas: {sell_gas_text}", callback_data="/sell_gas"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"Slippage: {slippage_text[:-1] if '%' in slippage_text else slippage_text}%",
                        callback_data="/slippage",
                    )
                ],
                # [InlineKeyboardButton("Advance Feature", callback_data='/advance_feature')],
                [InlineKeyboardButton("Add", callback_data="/add")],
                [InlineKeyboardButton("Back", callback_data="/copy_trade")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update._bot.send_message(
                chat_id=user_id,
                text=escape_markdown(
                    """To setup a new Copy Trade:
            - Assign a unique name or “tag” to your target wallet, to make it easier to identify.
            - Enter the target wallet address to copy trade.
            - Enter the percentage of the target's buy amount to copy trade with, or enter a specific SOL amount to always use.
            - Toggle on Copy Sells to copy the sells of the target wallet.
            - Click “Add” to create and activate the Copy Trade. """
                ),
                reply_markup=reply_markup,
            )
        else:
            user_context.set(user_id, "sell_gas_check", False)
            keyboard = [[InlineKeyboardButton(f"Retry", callback_data="/sell_gas")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f'Slippage must be entered as a number, e.g. "5" is 5%.',
                reply_markup=reply_markup,
            )
    else:
        if validate_public_key(text):
            account_info = solanaClient.get_balance(PublicKey(b58decode(text)))

            await update._bot.send_message(
                chat_id=update.effective_user.id, text=f"Click /start "
            )
            pass
        else:

            await update.message.reply_text(text=f"Invalid address.")


def process_buy_and_slippage_percentage(text: str):
    try:
        if "%" in text:
            res = float(text[:-1])
            return f"{res}%", True

        return f"{float(text)}", True
    except Exception as e:
        return "", False


def process_buy_and_sell(text: str):
    try:

        return f"{float(text)}", True
    except Exception as e:
        return "", False


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id
    data = user_context.get_all(user_id)
    context_data = user_context.get_context_data()
    if data:
        await update._bot.send_message(chat_id=user_id, text=context_data)
    else:
        await update._bot.send_message(chat_id=user_id, text=context_data)


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command_text = update.message.text
    user_id = update.effective_user.id

    match command_text:
        case "/start":
            user_context.clear_user(user_id)
            await start(update, context)
        case "/help":
            await help_command(update, context)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler(["start", "help"], callback=command_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    # asyncio.get_event_loop().create_task(monitor_changes())
    asyncio.get_event_loop().create_task(
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    )
    asyncio.run()


if __name__ == "__main__":
    main()
