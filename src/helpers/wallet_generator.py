from cryptography.fernet import Fernet
from solders.keypair import Keypair # type: ignore 
from src.config.config import SECRET_KEY
from src.helpers.common_instances import db_manager

def create_wallet_address():

    # Generate a new keypair
    keypair = Keypair()  
    public_key = keypair.pubkey()
    private_key = keypair.secret()
    
    cipher_suite = Fernet(key=SECRET_KEY)
    
    # Encrypt the private key
    encrypted_private_key = cipher_suite.encrypt(private_key)
    
    # Decrypt the private key to verify
    decrypted_private_key = cipher_suite.decrypt(encrypted_private_key)
    data = {
        'public_key': public_key,
        'encrypted_private_key':encrypted_private_key,
    }
    print(type(data['public_key']))
    return data
    # Print out the details
    # print(f"Public Key: {public_key}" ,type(public_key),'1111111111111')

def get_decrypted_private_and_public_key(telegram_id, wallet_address = None):

    cipher_suite = Fernet(key=SECRET_KEY)

    wallet_address = db_manager.get_wallet_by_telegram_id(telegram_id)
    encrypted_private_key = db_manager.get_wallet_encryped_key_by_telegram_id(telegram_id)

    decrypted_private_key = cipher_suite.decrypt(eval(encrypted_private_key))
    private_key = Keypair.from_seed(decrypted_private_key) # Private key as string
    return private_key, wallet_address

if __name__ == '__main__':
    wallet_private_key , wallet_address = get_decrypted_private_and_public_key(1295934535)
    print(wallet_private_key,wallet_address)
    
    
    pass


# {'public_key': Pubkey(
#     32mVNDR3HkFiYn7yGVuavwrWUg2L8mKNqZHP5kkN9GhP,
    # decrpyPK:  5rN7PEY75UZSK7KzJF1wJQUYTpX5RezmV8i3Xy49ZWMS8mnhXFcbBVPBea6Rp4ZtPHkxR5pnQz5sYogX3txzFYQ1,
# ), 'encrypted_private_key': b'gAAAAABmucEUCZCcwgBXv9uZyzz-b8epMmSvkemgRrgsrw1OvFDgGMN96sVfYLEMA0dXpfoc3oJDbbamq_ZS8mo8lbXSSLRSsgx35CPKumYkKlnfMgFaOoKaxZL1u2VDy9QExIwUKdc2'}