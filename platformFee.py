from src.db_connection.connectionpg import DatabaseManager
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from cryptography.fernet import Fernet
from src.config.config import SECRET_KEY
from src.config.config import SOLANA_URL, PLATFORM_WALLET
from solders.keypair import Keypair #type:ignore
from solders.pubkey import Pubkey #type:ignore
from solana.transaction import Transaction
import asyncio
from src.trades_logic.jupeter_trading import async_client
from src.helpers.common_instances import db_manager

cipher_suite = Fernet(key=SECRET_KEY)
# async_client = AsyncClient(SOLANA_URL)
# client = Client(SOLANA_URL)
from solders.system_program import transfer, TransferParams

async def transfer_fee(transfer_fee:int, telegram_id):
    """
    Platform Fees for swaping
    """
    try:
        print(type(transfer_fee), transfer_fee, telegram_id)
        #Fetching Private key from DB
        # telegram_id = 1484746944 # Hard Code Telegram ID for testing
        # transfer_fee = 0.0001 # Hard Code Trasnfer_fee for testing
        await asyncio.sleep(5)
        user_encrypted_private_key = db_manager.get_wallet_encryped_key_by_telegram_id(telegram_id)
        user_decrypted_private_key = cipher_suite.decrypt(eval(user_encrypted_private_key))
        user_private_key = Keypair.from_seed(user_decrypted_private_key) 

        user_wallet_address = db_manager.get_wallet_by_telegram_id(telegram_id)
        
        receiver = Pubkey.from_string(PLATFORM_WALLET)
        
        transfer_parameters = TransferParams(
        from_pubkey=Pubkey.from_string(user_wallet_address),
        to_pubkey=receiver,
        lamports=int(transfer_fee))

        sol_transfer = transfer(transfer_parameters)

        transaction = Transaction().add(sol_transfer)
        # try:
        print(user_private_key, 'user_private_key_rannnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
        # transaction_result = await async_client.send_transaction(transaction, user_private_key)
        # transaction_result = await async_client.send_transaction(transaction, user_private_key)
        transaction_result = await send_transaction_with_retry(transaction, user_private_key)
        # except Exception as e:
            # print(e, 'Error Here------------------------------------------------')

        # print("Transaction response: ", transaction_result)
        
        return 'Success'
    except Exception as e:
        print('Error in Transfer_fee:',e )
        pass


# import time
# from httpx import HTTPStatusError

async def send_transaction_with_retry(transaction, user_private_key, max_retries=5):
    retry = 0
    while retry  < max_retries:
        try:
            await async_client.send_transaction(transaction, user_private_key)
            break
        except Exception as e:
            print(f'Error in send_transaction retrying:{e}')
            await asyncio.sleep(5)
        finally:
            retry  = retry +1




if __name__ == "__main__":

    transer = transfer_fee(
                                transfer_fee=int(500),
                                telegram_id=1295934535,
                                # telegram_id=1484746944,
                                )
    asyncio.run(transer)
