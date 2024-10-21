import base58
import base64
import json

from solders import message
from solders.pubkey import Pubkey #type:ignore
from solders.keypair import Keypair #type:ignore
from solders.transaction import VersionedTransaction #type:ignore
from solders.rpc.errors import SendTransactionPreflightFailureMessage #type:ignore
from solders.rpc.responses import RpcSimulateTransactionResult #type:ignore
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client

from solana.rpc.commitment import Processed, Finalized
from solana.constants import LAMPORTS_PER_SOL, SYSTEM_PROGRAM_ID
from solana.transaction import Transaction
from jupiter_python_sdk.jupiter import Jupiter, Jupiter_DCA
import os
from cryptography.fernet import Fernet
import asyncio
from src.handlers import Wallet
from src.config.config import SOLANA_URL, PLATFORM_WALLET
from src.config.config import SECRET_KEY
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.system_program import transfer, TransferParams
import time
# from bot import db_manager


 
cipher_suite = Fernet(key=SECRET_KEY)
# db_manager = DatabaseManager()
async_client = AsyncClient(SOLANA_URL)
client = Client(SOLANA_URL)

# async def get_swap_quote(
#         input_mint,
#         output_mint,
#         amount_in_lamports,
#         telegram_id,
#         only_direct_routes=False
# ):
#     """
#     GET A SWAP Quote
#     """
#     try:

#         encrypted_private_key = db_manager.get_wallet_encryped_key_by_telegram_id(telegram_id)
#         decrypted_private_key = cipher_suite.decrypt(eval(encrypted_private_key))
#         private_key = Keypair.from_seed(decrypted_private_key) # Private key as string
#         jupiter = Jupiter(async_client, private_key)

#         quote_transaction_details = await jupiter.quote(
#             input_mint=input_mint,
#             output_mint=output_mint,
#             amount=int(amount_in_lamports),
#             only_direct_routes=only_direct_routes
#         )

#         data_token_price = await jupiter.get_token_price(input_mint=input_mint, output_mint=output_mint)
#         print(quote_transaction_details,'quote_transaction_details------')
#         # print(data_token_price)

#         return quote_transaction_details
#     except Exception as e:
#         print('Error in get_swap_quote method',e)
#         return None


async def execute_swap(
        input_mint,
        output_mint,
        amount_in_lamports,
        only_direct_routes = False
):
    """
    EXECUTE THE SWAP
    """
    try :
        encrypted_private_key = "b'gAAAAABmucEUCZCcwgBXv9uZyzz-b8epMmSvkemgRrgsrw1OvFDgGMN96sVfYLEMA0dXpfoc3oJDbbamq_ZS8mo8lbXSSLRSsgx35CPKumYkKlnfMgFaOoKaxZL1u2VDy9QExIwUKdc2'"
        decrypted_private_key = cipher_suite.decrypt(eval(encrypted_private_key))
        private_key = Keypair.from_seed(decrypted_private_key)
        jupiter = Jupiter(async_client, private_key)

        transaction_data = await jupiter.swap(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=int(amount_in_lamports),
            only_direct_routes=only_direct_routes,
            slippage_bps=20
        )
        # raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        # signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
        # signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        # opts = TxOpts(skip_preflight=False, preflight_commitment=Finalized, skip_confirmation=False)
        # result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        # print(result,'result------------------------------------------',result.to_json())
        # transaction_id = json.loads(result.to_json())['result']
        # print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
        transaction_id, error = await send_raw_transaction_with_retry_for_execute_swap(transaction_data, private_key)
        print(transaction_id,'transaction_id in execute_swap-----------------------------')

        if transaction_id:
            return transaction_id, 'Trade Successfull'
        else:
            return None, error
    except Exception as e:
        print('Error in execute swap method',e)
        return None, str(e)



async def send_raw_transaction_with_retry_for_execute_swap(transaction_data, private_key, max_retries=5):
    retry = 0
    error = 'error'
    transaction_id = None
    while retry < max_retries:
        try:
            raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
            signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
            signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
            opts = TxOpts(skip_preflight=False, preflight_commitment=Finalized, skip_confirmation=False, max_retries=10)
            result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
            transaction_id = json.loads(result.to_json())['result']
            
            if transaction_id:
                print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
                # return transaction_id
                break
            else:
                raise ValueError("Transaction did not return a valid transaction ID.")
        except Exception as e:
            error = e
            print(f'Error in send_raw_transaction_with_retry_for_execute_swap retrying: {e}')
            await asyncio.sleep(5)
        finally:
            retry += 1

        print(error, 'final error message in send_raw_transaction_with_retry_for_execute_swap')
    return transaction_id , str(error) # Explicitly return None if no transaction ID is obtained after retries


# async def transfer_fee(transfer_fee:int, telegram_id):
#     """
#     Platform Fees for swaping
#     """
#     try:
#         print(type(transfer_fee), transfer_fee, telegram_id)
#         #Fetching Private key from DB
#         # telegram_id = 1484746944 # Hard Code Telegram ID for testing
#         # transfer_fee = 0.0001 # Hard Code Trasnfer_fee for testing

#         user_encrypted_private_key = db_manager.get_wallet_encryped_key_by_telegram_id(telegram_id)
#         user_decrypted_private_key = cipher_suite.decrypt(eval(user_encrypted_private_key))
#         user_private_key = Keypair.from_seed(user_decrypted_private_key) 

#         user_wallet_address = db_manager.get_wallet_by_telegram_id(telegram_id)
        
#         receiver = Pubkey.from_string(PLATFORM_WALLET)
        
#         transfer_parameters = TransferParams(
#         from_pubkey=Pubkey.from_string(user_wallet_address),
#         to_pubkey=receiver,
#         lamports=int(transfer_fee))

#         sol_transfer = transfer(transfer_parameters)

#         transaction = Transaction().add(sol_transfer)
#         transaction_result = None
#         try:
#             print(user_private_key, 'user_private_key_rannnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
#             transaction_result = client.send_transaction(transaction, user_private_key)
#         except Exception as e:
#             print(e, 'Error Here------------------------------------------------')

#         print("Transaction response: ", transaction_result)
        
#         return 'Success'
#     except Exception as e:
#         print('Error in Transfer_fee:',e )
#         pass




if __name__ == '__main__':

    # asyncio.run(get_swap_quote(        
    #         # input_mint='So11111111111111111111111111111111111111112',
    #         input_mint='GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump',
    #         output_mint="So11111111111111111111111111111111111111112",
    #         # output_mint="GYKmdfcUmZVrqfcH1g579BGjuzSRijj3LBuwv79rpump",
    #         # amount_in_lamports=int(LAMPORTS_PER_SOL*0.01),
    #         amount_in_lamports=0,
    #         telegram_id=1295934535,
    #         only_direct_routes=False)) 

    
    asyncio.run(execute_swap(        
            # input_mint='So11111111111111111111111111111111111111112',
            input_mint='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
            output_mint="So11111111111111111111111111111111111111112",
            # output_mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            # amount_in_lamports=int(LAMPORTS_PER_SOL*0.0001),
            amount_in_lamports=int(109840388),
            only_direct_routes=False))  

    # transfer_data = transfer_fee(
    #      transfer_fee=0.01*LAMPORTS_PER_SOL,
    #      telegram_id=1484746944
    # )
    # asyncio.run(transfer_data)

    pass