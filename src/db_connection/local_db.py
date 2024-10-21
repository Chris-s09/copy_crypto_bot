import sqlite3
from solders.pubkey import Pubkey as PublicKey


class LocalDB:
    conn = None

    def __init__(self, seed=False) -> None:
        self.connect()
        if seed:
            self.seed()
        pass

    def connect(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        if self.conn is None:
            self.conn = sqlite3.connect("example.db")

    def seed(self):
        # Create a cursor object to execute SQL commands
        if self.conn is not None:
            cursor = self.conn.cursor()

            # Create the wallet table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS wallet (
                wallet_id INTEGER PRIMARY KEY,
                wallet_address,
                private_key
            )
            """
            )

            # Create the users table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                wallet_id INTEGER,
                FOREIGN KEY (wallet_id) REFERENCES wallet(wallet_id)
            )
            """
            )

            # Commit the changes and close the connection
            self.conn.commit()
            self.conn.close()

    def insert_wallet(self, wallet_address, private_key):
        if self.conn is not None:
            try:
                cur = self.conn.cursor()
                cur.execute(
                    """
                    INSERT INTO wallet (wallet_address)
                    VALUES ($1)
                    RETURNING wallet_id;
                """,
                    (str(wallet_address),),
                )
                wallet_id = cur.fetchone()[0]
                self.conn.commit()
                print(f"Wallet inserted successfully with wallet_id: {wallet_id}")
                cur.close()
                return wallet_id
            except Exception as e:
                print(f"The error '{e}' occurred")
                self.conn.rollback()
                return None
        return None

    def insert_user(self, telegram_id, wallet_id):
        if self.conn is not None:
            try:
                cur = self.conn.cursor()
                insert_user_query = """
                INSERT INTO users (telegram_id, wallet_id)
                VALUES ($1, $2)
                """
                cur.execute(insert_user_query, (telegram_id, wallet_id))
                self.conn.commit()
                print("User inserted successfully")
                cur.close()
            except Exception as e:
                print(f"The error '{e}' occurred")
                self.conn.rollback()

    def user_exists(self, telegram_id):
        if self.conn is not None:
            try:
                cur = self.conn.cursor()
                check_user_query = """
                SELECT COUNT(*) FROM users WHERE telegram_id = $1
                """
                cur.execute(check_user_query, (telegram_id,))
                count = cur.fetchone()[0]
                cur.close()
                return count > 0
            except Exception as e:
                print(f"The error '{e}' occurred")
                return False
        return False

    def user_exists_with_walletaddress(self, telegram_id):
        if self.conn is not None:
            try:
                cur = self.conn.cursor()
                check_user_query = """
                SELECT w.wallet_address
                FROM users u
                JOIN wallet w ON u.wallet_id = w.wallet_id
                WHERE u.telegram_id = $1
                """
                cur.execute(check_user_query, (telegram_id,))
                result = cur.fetchone()
                cur.close()

                if result is not None:
                    wallet_address = result[0]
                    return True, wallet_address
                else:
                    return False, None
            except Exception as e:
                print(f"The error '{e}' occurred")
                return False, None
        return False, None

    def validate_public_key(self, public_key):
        if public_key is not None:
            try:
                valid_public_key = PublicKey(public_key)
                print(f"Public Key {public_key} is valid.")
                return True
            except ValueError:
                print(f"Public Key {public_key} is invalid.")
                return False

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            print("Connection closed.")


# db = LocalDB()
# db.connect()
# db.seed()
