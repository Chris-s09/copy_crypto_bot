from typing import List, Dict
from solders.pubkey import Pubkey  # type:ignore
import requests
from base58 import b58decode
from decimal import Decimal
from enum import Enum
from src.db_connection.connectionpg import DatabaseManager
from solana.rpc.api import Client
from src.config.config import SOLANA_URL
from src.helpers.common_instances import db_manager,bot_logger


rpc_client = Client(SOLANA_URL)


class ChangeType(Enum):
    BUY = "buy"
    SELL = "sell"
    NO_CHANGE = "no_change"


class Token:
    address: str
    balance: int
    quantity: Decimal


class Wallet:
    url = "https://public-api.birdeye.so/v1/wallet/token_list"
    headers = {"x-chain": "solana", "X-API-KEY": "979df75b18664b468cf303427c2bd9e7"}

    wallet_address: str
    tokens: List[Token]

    def __init__(self, wallet_address) -> None:
        if wallet_address is None:
            raise ValueError("wallet_address cannot be None")
        self.wallet_address = wallet_address

    @staticmethod
    def get_token_overview(token_address):
        if token_address is None:
            raise ValueError("token_address cannot be None")
        try:
            url_token = f"https://public-api.birdeye.so/defi/token_overview?address={token_address}"

            headers = {
                "x-chain": "solana",
                "X-API-KEY": "979df75b18664b468cf303427c2bd9e7",
            }

            response = requests.get(url_token, headers=headers)
            # print(response.json().get('data').get('mc'))
            return response.json().get("data")
        except Exception as e:
            print("Error while getting the token info in get_token_overview:", e)
            return None

    @staticmethod
    def get_token_balance_data_in_wallet(wallet_address, token_address):
        if wallet_address is None or token_address is None:
            raise ValueError("wallet_address and token_address cannot be None")
        try:
            url_token = f"https://public-api.birdeye.so/v1/wallet/token_balance?wallet={wallet_address}&token_address={token_address}"

            headers = {
                "x-chain": "solana",
                "X-API-KEY": "979df75b18664b468cf303427c2bd9e7",
            }

            response = requests.get(url_token, headers=headers)
            # print(response.json().get('data').get('mc'))
            if response.status_code == 200:
                return response.json().get("data")
            else:
                return None
        except Exception as e:
            print("Error while getting the  get_token_balance_data_in_wallet:", e)
            return None

    @staticmethod
    def get_token_price(token_address):
        if token_address is None:
            raise ValueError("token_address cannot be None")
        try:
            url_token = (
                f"https://public-api.birdeye.so/defi/price?address={token_address}"
            )

            headers = {
                "x-chain": "solana",
                "X-API-KEY": "979df75b18664b468cf303427c2bd9e7",
            }

            response = requests.get(url_token, headers=headers)
            # print(response.json().get('data').get('mc'))
            if response.status_code == 200:
                return response.json().get("data")
            else:
                return None
        except Exception as e:
            print("Error while getting the token price :", e)
            return None

    def get_wallet_portfolio(self) -> None:
        try:
            data = self.fetch_data(self.url)
            if data is not None and data.get("success", False):
                # print(data.get('data').keys(),'data--------------')
                wallet_data = data.get("data")
                tokens_data = wallet_data.get("items")
                token_with_quntity = [
                    {
                        "address": item["address"],
                        "balance": item["balance"],
                        "quantity": item["uiAmount"],
                    }
                    for item in tokens_data
                ]
                return token_with_quntity
            else:
                return []
        except Exception as e:
            print("Error in get_wallet_portfolio:", e)

    def fetch_data(self, url):
        """Fetches data from the given URL."""
        try:
            response = requests.get(
                url, headers=self.headers, params={"wallet": self.wallet_address}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return None
        except Exception as e:
            print("Error in fetch_data:", e)
            return None

    @staticmethod
    def get_wallet_info_by_tgid(tgid):
        wallet_address = db_manager.get_wallet_by_telegram_id(tgid)
        if wallet_address is None:
            raise ValueError("wallet_address is None")
        balance = rpc_client.get_balance(
            pubkey=Pubkey.from_string(wallet_address)
        ).value

        return {"wallet_address": wallet_address, "balance": balance}


class Wallet_Prev_State(Wallet):
    def __init__(self, wallet_address) -> None:
        super().__init__(wallet_address)
        self.tokens = self.get_wallet_portfolio()


class Wallet_Current_State(Wallet):
    def __init__(self, wallet_address) -> None:
        super().__init__(wallet_address)
        self.tokens = self.get_wallet_portfolio()

    def compare_token_values(self, prev_state: Wallet):
        curr_tokens_balance = {}
        prev_tokens_balance = {}
        curr_balance = None
        prev_balance = None
        changes: List[Dict[str, ChangeType]] = []

        for current_token in self.tokens:
            if current_token is not None and current_token.get("address") is not None:
                curr_tokens_balance[current_token.get("address")] = current_token.get(
                    "balance"
                )

        for previous_token in prev_state.tokens:
            if previous_token is not None and previous_token.get("address") is not None:
                prev_tokens_balance[previous_token.get("address")] = previous_token.get(
                    "balance"
                )

        for curr_token in curr_tokens_balance:
            if (
                curr_token == "So11111111111111111111111111111111111111111"
                or curr_token == "So11111111111111111111111111111111111111112"
            ):
                continue
            if prev_tokens_balance.get(curr_token, None):
                prev_balance = prev_tokens_balance[curr_token]
                curr_balance = curr_tokens_balance.get(curr_token, 0)
                if (
                    prev_balance is not None
                    and curr_balance is not None
                    and prev_tokens_balance[curr_token]
                    != curr_tokens_balance[curr_token]
                ):
                    if prev_balance > curr_balance:
                        changes.append(
                            {
                                "wallet_address": self.wallet_address,
                                "token": curr_token,
                                "change_type": ChangeType.SELL,
                            }
                        )
                        bot_logger.log(
                            f"""if prev_balance > curr_balance:
                    
                        Token {curr_token} had a {ChangeType.SELL} change."""
                        )
                    else:
                        changes.append(
                            {
                                "wallet_address": self.wallet_address,
                                "token": curr_token,
                                "change_type": ChangeType.BUY,
                            }
                        )
                        bot_logger.log(
                            f"""else
                            if prev_balance < curr_balance:
                    
                        Token {curr_token} had a {ChangeType.BUY} change."""
                        )
                else:
                    changes.append(
                        {
                            "wallet_address": self.wallet_address,
                            "token": curr_token,
                            "change_type": ChangeType.NO_CHANGE,
                        }
                    )
            else:
                if curr_balance is not None:
                    changes.append(
                        {
                            "wallet_address": self.wallet_address,
                            "token": curr_token,
                            "change_type": ChangeType.BUY,
                        }
                    )
                    bot_logger.log(
                        f"""else:
                        if curr_balance is not None:   
                        Token {curr_token} had a {ChangeType.BUY} change."""
                    )

        for prev_token in prev_tokens_balance:
            if curr_tokens_balance.get(prev_token, None) == None:
                changes.append({"token": prev_token, "change_type": ChangeType.SELL})
                bot_logger.log(
                    f"""
                    for prev_token in prev_tokens_balance:
            if curr_tokens_balance.get(prev_token, None) == None:
            
                    Token {prev_token} had a {ChangeType.SELL} change.
                    curr_token={curr_tokens_balance}"""
                )
        # for change in changes:
        #       print(f'Token {change["token"]} had a {change["change_type"]} change.')

        changes = [
            change
            for change in changes
            if change["change_type"] != ChangeType.NO_CHANGE
        ]

        return changes if changes is not None else []


if __name__ == "__main__":
    # wallet = Wallet('6ZpYTMSSK6TUcGVbP1zK4G1j9M1GjXSiWXEUPzj5gAyG')
    # # print(wallet.get_token_balance_data_in_wallet(wallet_address='6ZpYTMSSK6TUcGVbP1zK4G1j9M1GjXSiWXEUPzj5gAyG',token_address='EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm'))
    # print(wallet.get_token_price('So11111111111111111111111111111111111111112'))
    pass
