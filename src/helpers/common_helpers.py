
from solders.pubkey import Pubkey as PublicKey


def validate_public_key(public_key:str):
        print(public_key)
        if public_key is not None:
            try:
                valid_public_key = PublicKey.from_string(public_key)
                print(f"Public Key {public_key} is valid.")
                return True
            except Exception as e:
                print(f"Public Key {public_key} is invalid.")
                return False