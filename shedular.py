from src.db_connection.connectionpg import DatabaseManager
from src.handlers.Wallet import Wallet_Prev_State, Wallet_Current_State
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
import asyncio
import datetime
import time
from src.handlers.Alert_Handler import (
    get_tg_ids_by_moniter_wallet,
    sendMessage,
    alert_manager,
)
from src.helpers.constants import ALERT_MESSAGE
from src.handlers.Wallet import ChangeType
import json

all_wallets = []
last_db_fetched_seconds = time.time()


async def update_wallets_to_monitor():
    global all_wallets
    global last_db_fetched_seconds
    db_client = DatabaseManager()
    all_wallets = db_client.get_all_monitored_wallets()
    last_db_fetched_seconds = time.time()
    return all_wallets


async def monitor_changes():
    """Monitors changes in data fetched from the given URL."""
    await update_wallets_to_monitor()
    prev_states: dict = {}
    processed_wallets = []
    global all_wallets
    for wallet in all_wallets:
        processed_wallets.append(
            {
                "telegram_id": wallet[0].get("telegram_id"),
                "target_wallet": wallet[0].get("target_wallet"),
            }
        )
    for wallet in processed_wallets:
        await asyncio.sleep(3)
        target_wallet = wallet.get("target_wallet", None)
        prev_state = Wallet_Prev_State(target_wallet)
        prev_states[target_wallet] = prev_state

    while True:
        await asyncio.sleep(5)
        print(f"Checking for changes at {datetime.datetime.now()}")
        # latest_data = await fetch_data(url)
        try:
            all_wallets = await update_wallets_to_monitor()
            print(
                "Updating wallets -----------------------------------", len(prev_states)
            )

            for wallet_address, prev_state in prev_states.items():
                curr_state = Wallet_Current_State(wallet_address)
                # if time.time() - last_db_fetched_seconds >= 60:

                await asyncio.sleep(5)
                changes = curr_state.compare_token_values(prev_state)

                if len(changes) > 0:
                    print("take action", wallet_address)
                    tg_ids = get_tg_ids_by_moniter_wallet(wallet_address)

                    for change in changes:
                        change_type = change.get("change_type", "unsupported")
                        formatted_change_type = "unsupported"

                        if ChangeType.BUY == change_type:
                            formatted_change_type = "BUY"
                        elif ChangeType.SELL == change_type:
                            formatted_change_type = "SELL"

                        for tg_id in tg_ids:
                            alert_id = alert_manager.generate_random_id()
                            token = change.get("token", "unsupported")
                            if (
                                token == "So11111111111111111111111111111111111111111"
                                or token
                                == "So11111111111111111111111111111111111111112"
                            ):
                                continue
                            alert_manager.set(
                                alert_id,
                                {
                                    "wallet_address": wallet_address,
                                    "change_type": formatted_change_type,
                                    "token": token,
                                    "telegram_id": tg_id,
                                },
                            )

                            keyboard = [
                                [
                                    InlineKeyboardButton(
                                        "Execute",
                                        callback_data=f"/execute_swap {alert_id}",
                                    )
                                ],
                            ]

                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await sendMessage(
                                tgId=tg_id,
                                text=ALERT_MESSAGE.format(
                                    wallet_address,
                                    formatted_change_type,
                                    change.get("token", "unsupported"),
                                ),
                                reply_markup=reply_markup,
                            )
                            asyncio.create_task(
                                alert_manager.clear_id_after_delay(alert_id)
                            )

                    prev_states[wallet_address].tokens = curr_state.tokens
                else:
                    print("No Change for ", wallet_address)
                    continue

            for wallet in all_wallets:
                _wallet_address = wallet[0].get("target_wallet")
                if not prev_states.get(_wallet_address, None):
                    print("added wallet", _wallet_address)
                    prev_states[_wallet_address] = Wallet_Prev_State(_wallet_address)

            for wallet_address, prev_state in prev_states.items():
                FOUND = False
                for wallet in all_wallets:
                    _wallet_address = wallet[0].get("target_wallet")
                    if wallet_address == _wallet_address:
                        FOUND = True
                        # print('Found wallet_address breaking from loop', _wallet_address, wallet_address)
                        break
                if not FOUND:
                    print("deleted wallet", _wallet_address)
                    del prev_states[wallet_address]
        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    asyncio.run(monitor_changes())
