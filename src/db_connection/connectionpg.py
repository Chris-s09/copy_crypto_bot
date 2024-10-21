import psycopg2
from typing import List
from psycopg2 import OperationalError
from solders.pubkey import Pubkey as PublicKey  # type:ignore
from cryptography.fernet import Fernet


class DatabaseManager:
    _instance = None

    def __init__(cls):
        if not cls._instance:
            cls._instance = cls
            cls.conn = None
            cls._initialize_connection()

    def _initialize_connection(self):
        try:
            if self.conn is not None and self.conn.closed:
                raise OperationalError("Connection to PostgreSQL DB was closed")
            if self.conn is None:
                self.conn = psycopg2.connect(
                    dbname="cryptobot_dev",
                    user="dev_db_user",
                    password="g5zlesmH4rRmNvw",
                    host="crypto-bot-database-dev.cluster-c70a02km6jqg.eu-north-1.rds.amazonaws.com",
                    port="5432",
                )
            if self.conn is None:
                raise OperationalError("Connection to PostgreSQL DB failed")
            print("Connection to PostgreSQL DB successful")
        except OperationalError as e:
            print(f"The error occurred in _initialize_connection '{e}' ")
            self.conn = None

    def check_connection(self):
        if self.conn is None or self.conn.closed:
            print("creating new connection")
            self._initialize_connection()
        try:
            if self.conn is None or self.conn.closed:
                raise OperationalError("Connection to PostgreSQL DB was closed")
        except OperationalError as e:
            print(f"The error occurred in check_connection '{e}' ")
            self.conn = None
        return self.conn

    def insert_wallet(self, wallet_address, private_key):
        if wallet_address is None or private_key is None:
            raise TypeError("wallet_address and private_key must not be None")
        self.check_connection()
        if self.conn:
            try:
                cur = self.conn.cursor()
                insert_wallet_query = """
                INSERT INTO wallet (wallet_address, private_key)
                VALUES (%s, %s)
                RETURNING wallet_id
                """
                cur.execute(
                    insert_wallet_query, (str(wallet_address), str(private_key))
                )
                wallet_id = cur.fetchone()[0]
                self.conn.commit()
                print(f"Wallet inserted successfully with wallet_id: {wallet_id}")
                cur.close()
                return wallet_id
            except psycopg2.Error as e:
                print(f"The error occurred in insert_wallet '{e}' ")
                self.conn.rollback()
                return None
        return None

    def insert_user(self, telegram_id, wallet_id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None or wallet_id is None:
            raise TypeError("telegram_id and wallet_id must not be None")

        try:
            cur = self.conn.cursor()
            insert_user_query = """
            INSERT INTO users (telegram_id, wallet_id)
            VALUES (%s, %s)
            """
            cur.execute(insert_user_query, (telegram_id, wallet_id))
            self.conn.commit()
            print("User inserted successfully")
            cur.close()
        except psycopg2.Error as e:
            print(f"The error occurred in insert_user '{e}' ")
            self.conn.rollback()

    def user_exists(self, telegram_id):
        self.check_connection()

        if self.conn is not None:
            try:
                cur = self.conn.cursor()
                check_user_query = """
                SELECT COUNT(*) FROM users WHERE telegram_id = %s
                """
                cur.execute(check_user_query, (telegram_id,))
                count = cur.fetchone()[0]
                cur.close()
                return count > 0
            except psycopg2.Error as e:
                print(f"The error occurred in user_exists '{e}' ")
                self.conn.rollback()
                return False
        return False

    def get_wallet_by_telegram_id(self, telegram_id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
            SELECT w.wallet_address
            FROM users u
            JOIN wallet w ON u.wallet_id = w.wallet_id
            WHERE u.telegram_id = %s
            """
            cur.execute(check_user_query, (telegram_id,))
            result = cur.fetchone()
            cur.close()

            if result is not None:
                wallet_address = result[0]
                if wallet_address is not None:
                    return wallet_address
                else:
                    return None
            else:
                return None
        except psycopg2.Error as e:
            print(f"The error occurred in get_wallet_by_telegram_id '{e}' ")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"An error occurred in get_wallet_by_telegram_id: {e}")
            return None

    def get_wallet_id_by_telegram_id(self, telegram_id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
                SELECT w.wallet_id
                FROM users u
                JOIN wallet w ON u.wallet_id = w.wallet_id
                WHERE u.telegram_id = %s
                """
            cur.execute(check_user_query, (telegram_id,))
            result = cur.fetchone()
            cur.close()

            if result is not None:
                wallet_id = result[0]
                if wallet_id is not None:
                    return wallet_id
                else:
                    return None
            else:
                return None
        except psycopg2.Error as e:
            print(f"The error occurred in get_wallet_by_telegram_id '{e}' ")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"An error occurred in get_wallet_by_telegram_id: {e}")
            return None

    def get_wallet_encryped_key_by_telegram_id(self, telegram_id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
            SELECT w.private_key
            FROM users u
            JOIN wallet w ON u.wallet_id = w.wallet_id
            WHERE u.telegram_id = %s
            """
            cur.execute(check_user_query, (telegram_id,))
            result = cur.fetchone()
            cur.close()

            if result is not None:
                wallet_address = result[0]
                if wallet_address is not None:
                    return wallet_address
                else:
                    return None
            else:
                return None
        except psycopg2.Error as e:
            print(
                f"The error occurred in get_wallet_encryped_key_by_telegram_id '{e}' "
            )
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"An error occurred in get_wallet_encryped_key_by_telegram_id: {e}")
            return None

    def delete_all_users(self):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
            delete from users where 1=1
            """
            cur.execute(
                check_user_query,
            )
            print("Users Deleted!")
            cur.close()

        except psycopg2.Error as e:
            print(f"The error occurred in delete_all_users '{e}' ")
            self.conn.rollback()
            return False, None
        except Exception as e:
            print(f"An error occurred in delete_all_users: {e}")
            return False, None

    def delete_user(self, telegram_id: int):
        """
        Deletes a user from the users table.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            cur = self.conn.cursor()
            query = """
            Delete from users where telegram_id = %s
            """
            cur.execute(query, (telegram_id,))
            cur.close()
            print("user deleted")
        except psycopg2.Error as e:
            print(f"The error occurred in delete_user '{e}' ")
            self.conn.rollback()
        except Exception as e:
            print(f"An error occurred in delete_user: {e}")

    def get_users(self):
        """
        Retrieves a list of all users from the users table.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
            select * from users
            """
            cur.execute(
                check_user_query,
            )
            result = cur.fetchall()
            cur.close()

            if result is not None:
                return result
            else:
                return None

        except psycopg2.Error as e:
            print(f"The error occurred in get_users '{e}' ")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"An error occurred in get_users: {e}")
            return None

    def get_target_wallets_by_tg(self, telegram_id):
        """
        Retrieves a list of all target wallets for a telegram user from the monitor_wallets table.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            cur = self.conn.cursor()
            check_user_query = """
            Select target_wallet from monitor_wallets where telegram_id = %s
            """
            cur.execute(check_user_query, (telegram_id,))
            result = cur.fetchall()
            cur.close()

            if result is not None:
                return result
            else:
                return None

        except psycopg2.Error as e:
            print(f"The error occurred in get_target_wallets_by_tg '{e}' ")
            self.conn.rollback()
            return None
        except AttributeError as e:
            print(f"AttributeError in get_target_wallets_by_tg: {e}")
            return None
        except Exception as e:
            print(f"An error occurred in get_target_wallets_by_tg: {e}")
            return None

    def add_tag(self, telegram_id, tag):
        """
        Adds a new record to the monitor_wallets table with the given telegram_id and tag.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if tag is None:
            raise TypeError("tag must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Insert a new record
            insert_query = """
            INSERT INTO monitor_wallets (telegram_id, tag) VALUES (%s, %s);
            """
            cur.execute(insert_query, (telegram_id, tag))

            # Commit the transaction
            self.conn.commit()

            print("Record added successfully for tag.")
        except psycopg2.Error as e:
            print(f"The error occurred in add_tag '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in add_tag: {e}")
        except Exception as e:
            print(f"An error occurred in add_tag: {e}")

    def update_tag(self, telegram_id, tag, id):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                # Check if the record exists
                check_query = """
                SELECT EXISTS (
                    SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND tag = %s AND  id = %s
                );
                """
                cur.execute(check_query, (telegram_id, tag, id))
                exists = cur.fetchone()[0]

                if exists:
                    # Update the record
                    update_query = """
                    UPDATE monitor_wallets SET tag = %s WHERE telegram_id = %s AND id = %s;
                    """
                    cur.execute(update_query, (tag, telegram_id, tag, id))
                else:
                    print(
                        f"Id {id} for telegram_id {telegram_id} where tag is {tag} doesn't exists"
                    )

                # Commit the transaction
                self.conn.commit()

                print("Record updated successfully for tag.")
            except Exception as e:
                print(f"An error occurred in update_tag: {e}")

    def add_target_wallet(self, telegram_id, target_wallet):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                # Insert a new record
                insert_query = """
                INSERT INTO monitor_wallets (telegram_id, target_wallet) VALUES (%s, %s);
                """
                cur.execute(insert_query, (telegram_id, target_wallet))

                # Commit the transaction
                self.conn.commit()

                print("Record added successfully for target_wallet.")
            except Exception as e:
                print(f"An error occurred in add_target_wallet: {e}")

    def update_target_wallet(self, telegram_id, target_wallet, id):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                # Check if the record exists
                check_query = """
                SELECT EXISTS (
                    SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND target_wallet = %s AND id = %s
                );
                """
                cur.execute(check_query, (telegram_id, target_wallet, id))
                exists = cur.fetchone()[0]

                if exists:
                    # Assuming you want to update a specific field, e.g., tag
                    update_query = """
                    UPDATE monitor_wallets SET target_wallet = %s WHERE telegram_id = %s AND id = %s;
                    """
                    cur.execute(update_query, (telegram_id, target_wallet))
                else:
                    print(
                        f"telegram_id {telegram_id} for updating target_wallet {target_wallet} Doesn't exists"
                    )

                # Commit the transaction
                self.conn.commit()

                print("Record updated successfully for target_wallet.")
            except Exception as e:
                print(f"An error occurred in update_target_wallet: {e}")

    def add_buy_percentage(self, telegram_id, buy_percentage):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                # Insert a new record with the given buy percentage
                insert_query = """
                INSERT INTO monitor_wallets (telegram_id, buy_percentage) VALUES (%s, %s,);
                """
                cur.execute(insert_query, (telegram_id, buy_percentage))

                # Commit the transaction
                self.conn.commit()

                print("Record added successfully.")
            except Exception as e:
                print(f"An error occurred in add_buy_percentage: {e}")

    def update_buy_percentage(self, telegram_id, buy_percentage, id):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                # Check if the record exists
                check_query = """
                SELECT EXISTS (
                    SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
                );
                """
                cur.execute(check_query, (telegram_id, id))
                exists = cur.fetchone()[0]

                if exists:
                    # Update the record with the new buy percentage
                    update_query = """
                    UPDATE monitor_wallets SET buy_percentage = %s WHERE telegram_id = %s AND id = %s;
                    """
                    cur.execute(update_query, (buy_percentage, telegram_id, id))
                else:
                    print("Does'nt Exists for updating buy_percentage")

                # Commit the transaction
                self.conn.commit()

                print("Record updated successfully.")
            except Exception as e:
                print(f"An error occurred in update_buy_percentage: {e}")

    def add_sell_gas(self, telegram_id, sell_gas):
        """
        Adds a new record to the monitor_wallets table with the given telegram_id and sell_gas.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if sell_gas is None:
            raise TypeError("sell_gas must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Insert a new record
            insert_query = """
            INSERT INTO monitor_wallets (telegram_id, sell_gas) VALUES (%s, %s);
            """
            cur.execute(insert_query, (telegram_id, sell_gas))

            # Commit the transaction
            self.conn.commit()

            print("Record added successfully for sell_gas.")
        except psycopg2.Error as e:
            print(f"The error occurred in add_sell_gas '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in add_sell_gas: {e}")
        except Exception as e:
            print(f"An error occurred in add_sell_gas: {e}")

    def update_sell_gas(self, telegram_id, sell_gas, id):
        """
        Updates a record in the monitor_wallets table with the given telegram_id and sell_gas values.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if sell_gas is None:
            raise TypeError("sell_gas must not be None")

        if id is None:
            raise TypeError("id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Check if the record exists
            check_query = """
            SELECT EXISTS (
                SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
            );
            """
            cur.execute(check_query, (telegram_id, id))
            exists = cur.fetchone()[0]

            if exists:
                # Update the record with the new sell gas value
                update_query = """
                UPDATE monitor_wallets SET sell_gas = %s WHERE telegram_id = %s AND id = %s;
                """
                cur.execute(update_query, (sell_gas, telegram_id, id))
            else:
                print(f"sell_gas {sell_gas} does'nt exist")

            # Commit the transaction
            self.conn.commit()

            print("Record updated successfully for sell_gas.")
        except psycopg2.Error as e:
            print(f"The error occurred in update_sell_gas '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in update_sell_gas: {e}")
        except Exception as e:
            print(f"An error occurred in update_sell_gas: {e}")

    def add_buy_gas(self, telegram_id, buy_gas):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if buy_gas is None:
            raise TypeError("buy_gas must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Insert a new record with the given buy gas value
            insert_query = """
            INSERT INTO monitor_wallets (telegram_id, buy_gas) VALUES (%s, %s);
            """
            cur.execute(insert_query, (telegram_id, buy_gas))

            # Commit the transaction
            self.conn.commit()

            print("Record added successfully for buy_gas.")
        except psycopg2.Error as e:
            print(f"The error occurred in add_buy_gas '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in add_buy_gas: {e}")
        except Exception as e:
            print(f"An error occurred in add_buy_gas: {e}")

    def delete_wallet_by_telegram_id(self, telegram_id: int, wallet_id: int) -> None:

        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE telegram_id = %s", (telegram_id,))
            cursor.execute(
                "DELETE FROM monitor_wallets WHERE telegram_id = %s", (telegram_id,)
            )
            cursor.execute("DELETE FROM wallet WHERE wallet_id = %s", (wallet_id,))
        self.conn.commit()

    def deleted_wallet_having_balance(self, telegram_id: int) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE telegram_id = %s", (telegram_id,))

    def update_buy_gas(self, telegram_id, buy_gas, id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if buy_gas is None:
            raise TypeError("buy_gas must not be None")

        if id is None:
            raise TypeError("id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Check if the record exists
            check_query = """
            SELECT EXISTS (
                SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
            );
            """
            cur.execute(check_query, (telegram_id, id))
            exists = cur.fetchone()[0]

            if exists:
                # Update the record with the new sell gas value
                update_query = """
                UPDATE monitor_wallets SET buy_gas = %s WHERE telegram_id = %s AND id = %s;
                """
                cur.execute(update_query, (buy_gas, telegram_id, id))
            else:
                print(f"buy_gas {buy_gas} does'nt exist")

            # Commit the transaction
            self.conn.commit()

            print("Record updated successfully for buy_gas.")
        except psycopg2.Error as e:
            print(f"The error occurred in update_buy_gas '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in update_buy_gas: {e}")
        except TypeError as e:
            print(f"TypeError in update_buy_gas: {e}")
        except ValueError as e:
            print(f"ValueError in update_buy_gas: {e}")
        except Exception as e:
            print(f"An error occurred in update_buy_gas: {e}")

    def add_slippage(self, telegram_id, slippage):
        """
        Adds a new record to the monitor_wallets table with the given telegram_id and slippage.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if slippage is None:
            raise TypeError("slippage must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Insert a new record with the given buy gas value
            insert_query = """
            INSERT INTO monitor_wallets (telegram_id, slippage) VALUES (%s, %s);
            """
            cur.execute(insert_query, (telegram_id, slippage))

            # Commit the transaction
            self.conn.commit()

            print("Record added successfully for slippage.")
        except psycopg2.Error as e:
            print(f"The error occurred in add_slippage '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in add_slippage: {e}")
        except TypeError as e:
            print(f"TypeError in add_slippage: {e}")
        except ValueError as e:
            print(f"ValueError in add_slippage: {e}")
        except Exception as e:
            print(f"An error occurred in add_slippage: {e}")

    def update_slippage(self, telegram_id, slippage, id):
        """
        Updates a record in the monitor_wallets table with the given telegram_id and slippage values.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if slippage is None:
            raise TypeError("slippage must not be None")

        if id is None:
            raise TypeError("id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Check if the record exists
            check_query = """
            SELECT EXISTS (
                SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
            );
            """
            cur.execute(check_query, (telegram_id, id))
            exists = cur.fetchone()[0]

            if exists:
                # Update the record with the new sell gas value
                update_query = """
                UPDATE monitor_wallets SET slippage = %s WHERE telegram_id = %s AND id = %s;
                """
                cur.execute(update_query, (slippage, telegram_id, id))
            else:
                print(f"slippage {slippage} does'nt exist")

            # Commit the transaction
            self.conn.commit()

            print("Record updated successfully for slippage.")
        except psycopg2.Error as e:
            print(f"The error occurred in update_slippage '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in update_slippage: {e}")
        except TypeError as e:
            print(f"TypeError in update_slippage: {e}")
        except ValueError as e:
            print(f"ValueError in update_slippage: {e}")
        except Exception as e:
            print(f"An error occurred in update_slippage: {e}")

    def update_copy_sell(self, telegram_id, copy_sell, id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if copy_sell is None:
            raise TypeError("copy_sell must not be None")

        if id is None:
            raise TypeError("id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Check if the record exists
            check_query = """
            SELECT EXISTS (
                SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
            );
            """
            cur.execute(check_query, (telegram_id, id))
            exists = cur.fetchone()[0]

            if exists:
                cur.execute(
                    """
                UPDATE monitor_wallets SET copy_sell = %s WHERE telegram_id = %s AND id = %s
                """,
                    (copy_sell, telegram_id, id),
                )
                self.conn.commit()
                print("Copy sell status updated successfully.")
            else:
                print("No existing record found to update for copy_sell.")
        except psycopg2.Error as e:
            print(f"The error occurred in update_copy_sell '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in update_copy_sell: {e}")
        except TypeError as e:
            print(f"TypeError in update_copy_sell: {e}")
        except ValueError as e:
            print(f"ValueError in update_copy_sell: {e}")
        except Exception as e:
            print(f"An error occurred in update_copy_sell: {e}")

    def add_all_trade_data(
        self,
        telegram_id,
        target_wallet,
        tag,
        buy_percentage,
        copy_sell,
        sell_gas,
        slippage,
        buy_gas,
        is_active=True,
        max_buy_amount=None,
        exclude_pump_fun_tokens=None,
        min_liquidity=None,
        min_mcap=None,
        max_mcap=None,
    ):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if target_wallet is None:
            raise TypeError("target_wallet must not be None")

        # if tag is None:
        #     raise TypeError("tag must not be None")

        # if buy_percentage is None:
        #     raise TypeError("buy_percentage must not be None")

        # if copy_sell is None:
        #     raise TypeError("copy_sell must not be None")

        # if sell_gas is None:
        #     raise TypeError("sell_gas must not be None")

        # if slippage is None:
        #     raise TypeError("slippage must not be None")

        # if buy_gas is None:
        #     raise TypeError("buy_gas must not be None")

        # if max_buy_amount is None:
        #     raise TypeError("max_buy_amount must not be None")

        # if exclude_pump_fun_tokens is None:
        #     raise TypeError("exclude_pump_fun_tokens must not be None")

        # if min_liquidity is None:
        #     raise TypeError("min_liquidity must not be None")

        # if min_mcap is None:
        #     raise TypeError("min_mcap must not be None")

        # if max_mcap is None:
        #     raise TypeError("max_mcap must not be None")

        # if is_active is None:
        #     raise TypeError("is_active must not be None")

        # if not isinstance(is_active, bool):
        #     raise TypeError("is_active must be a boolean")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Insert a new record with the given buy gas value
            insert_query = """
            INSERT INTO monitor_wallets (telegram_id, target_wallet, tag, buy_percentage, copy_sell, sell_gas, slippage, buy_gas, max_buy_amount, exclude_pump_fun_tokens, min_liquidity, min_mcap, max_mcap, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(
                insert_query,
                (
                    telegram_id,
                    target_wallet,
                    tag,
                    buy_percentage,
                    copy_sell,
                    sell_gas,
                    slippage,
                    buy_gas,
                    max_buy_amount,
                    exclude_pump_fun_tokens,
                    min_liquidity,
                    min_mcap,
                    max_mcap,
                    is_active,
                ),
            )

            # Commit the transaction
            self.conn.commit()

            print("Record added successfully for add_all_trade_data.")
        except psycopg2.Error as e:
            print(f"The error occurred in add_all_trade_data '{e}' ")
            self.conn.rollback()
        except AttributeError as e:
            print(f"AttributeError in add_all_trade_data: {e}")
        except TypeError as e:
            print(f"TypeError in add_all_trade_data: {e}")
        except ValueError as e:
            print(f"ValueError in add_all_trade_data: {e}")
        except Exception as e:
            print(f"An error occurred in add_all_trade_data: {e}")

    def delete_all_monitor_wallets_data(self, telegram_id, id):
        self.check_connection()

        if self.conn:
            try:
                # Connect to the PostgreSQL database
                cur = self.conn.cursor()

                if telegram_id is not None and id is not None:
                    check_query = """
                    SELECT EXISTS (
                        SELECT 1 FROM monitor_wallets WHERE telegram_id = %s AND id = %s
                    );
                    """
                    cur.execute(check_query, (telegram_id, id))
                    exists = cur.fetchone()[0]

                    if exists:
                        cur.execute(
                            """
                        DELETE FROM monitor_wallets WHERE telegram_id = %s AND id = %s
                        """,
                            (telegram_id, id),
                        )
                        self.conn.commit()
                        print("Specific record deleted successfully.")
                    else:
                        print(
                            f"No existing record found to delete for the specified ID {id} and Telegram ID {telegram_id}"
                        )
                else:
                    print(
                        f"Error in delete_all_monitor_wallets_data: telegram_id and id must not be null"
                    )
            except psycopg2.Error as e:
                print(f"The error occurred in delete_all_monitor_wallets_data '{e}' ")
                self.conn.rollback()
            except AttributeError as e:
                print(f"AttributeError in delete_all_monitor_wallets_data: {e}")
            except TypeError as e:
                print(f"TypeError in delete_all_monitor_wallets_data: {e}")
            except ValueError as e:
                print(f"ValueError in delete_all_monitor_wallets_data: {e}")
            except Exception as e:
                print(f"An error occurred in delete_all_monitor_wallets_data: {e}")

    def get_wallet_record_by_telegram_id_(self, telegram_id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Query to select records by telegram_id and target_wallet
            select_query = """
            SELECT * FROM monitor_wallets WHERE telegram_id = %s;
            """
            cur.execute(select_query, (telegram_id,))

            # Fetch the result
            result = cur.fetchall()

            if result is None:
                return []  # Return an empty list if no matching records found
            else:
                return result  # Return all matching records
        except psycopg2.Error as e:
            print(f"The error occurred in get_wallet_record_by_telegram_id_ '{e}' ")
            return []
        except AttributeError as e:
            print(f"AttributeError in get_wallet_record_by_telegram_id_: {e}")
            return []
        except TypeError as e:
            print(f"TypeError in get_wallet_record_by_telegram_id_: {e}")
            return []
        except ValueError as e:
            print(f"ValueError in get_wallet_record_by_telegram_id_: {e}")
            return []
        except Exception as e:
            print(f"An error occurred in get_wallet_record_by_telegram_id_: {e}")
            return []

    def get_wallet_records_with_column_names_for_telegram_id(self, telegram_id, id):
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if id is None:
            raise TypeError("id must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Query to select records by telegram_id and target_wallet
            select_query = """
            SELECT * FROM monitor_wallets WHERE telegram_id = %s AND id = %s;
            """
            cur.execute(select_query, (telegram_id, id))

            # Get column names
            column_names = [desc[0] for desc in cur.description]

            # Fetch the result
            result = cur.fetchall()
            # print(result)
            if result is None:
                return []  # Return an empty list if no matching records found
            else:
                # Combine column names with data rows
                combined_result = [
                    (dict(zip(column_names, row)), row) for row in result
                ]
                return combined_result  # Return combined result
        except psycopg2.Error as e:
            print(
                f"The error occurred in get_wallet_records_with_column_names_for_telegram_id '{e}' "
            )
            return []
        except AttributeError as e:
            print(
                f"AttributeError in get_wallet_records_with_column_names_for_telegram_id: {e}"
            )
            return []
        except TypeError as e:
            print(
                f"TypeError in get_wallet_records_with_column_names_for_telegram_id: {e}"
            )
            return []
        except ValueError as e:
            print(
                f"ValueError in get_wallet_records_with_column_names_for_telegram_id: {e}"
            )
            return []
        except Exception as e:
            print(
                f"An error occurred in get_wallet_records_with_column_names_for_telegram_id: {e}"
            )
            return []

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")

    def get_all_monitored_wallets(self):
        """
        Retrieves a list of all monitored wallets from the monitor_wallets table.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Query to select records by telegram_id and target_wallet
            select_query = """
            SELECT * FROM monitor_wallets where is_active = true;
            """
            cur.execute(select_query)

            # Get column names
            column_names = [desc[0] for desc in cur.description]

            result = cur.fetchall()
            if result is None:
                return []  # Return an empty list if no matching records found
            else:
                # Combine column names with data rows
                combined_result = [
                    (dict(zip(column_names, row)), row) for row in result
                ]
                return combined_result  # Return combined result
        except psycopg2.Error as e:
            print(f"The error occurred in get_all_monitored_wallets '{e}' ")
            return []
        except AttributeError as e:
            print(f"AttributeError in get_all_monitored_wallets: {e}")
            return []
        except TypeError as e:
            print(f"TypeError in get_all_monitored_wallets: {e}")
            return []
        except ValueError as e:
            print(f"ValueError in get_all_monitored_wallets: {e}")
            return []
        except Exception as e:
            print(f"An error occurred in get_all_monitored_wallets: {e}")
            return []

    def get_tgid_by_moniter_wallet(self, wallet_address: str = "") -> List:
        """
        Retrieves a list of telegram ids of users who are monitoring a wallet.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if wallet_address is None:
            raise TypeError("wallet_address must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Query to select records by telegram_id and target_wallet
            select_query = """
            SELECT telegram_id FROM monitor_wallets WHERE target_wallet = %s;
            """
            cur.execute(select_query, (wallet_address,))

            # Get column names
            column_names = [desc[0] for desc in cur.description]

            result = cur.fetchall()
            if result is None:
                return []  # Return an empty list if no matching records found
            else:
                # Combine column names with data rows
                combined_result = [
                    (dict(zip(column_names, row)), row) for row in result
                ]
                return combined_result  # Return combined result
        except psycopg2.Error as e:
            print(f"The error occurred in get_tgid_by_moniter_wallet '{e}' ")
            return []
        except AttributeError as e:
            print(f"AttributeError in get_tgid_by_moniter_wallet: {e}")
            return []
        except TypeError as e:
            print(f"TypeError in get_tgid_by_moniter_wallet: {e}")
            return []
        except ValueError as e:
            print(f"ValueError in get_tgid_by_moniter_wallet: {e}")
            return []
        except Exception as e:
            print(f"An error occurred in get_tgid_by_moniter_wallet: {e}")
            return []

    def get_monitor_wallet_by_telegram_id_token(self, telegram_id, wallet_address):
        """
        Retrieves a list of all monitored wallets and their respective tokens for a telegram user from the monitor_wallets table.
        """
        self.check_connection()

        if self.conn is None:
            raise ValueError("Connection to PostgreSQL DB is None")

        if telegram_id is None:
            raise TypeError("telegram_id must not be None")

        if wallet_address is None:
            raise TypeError("wallet_address must not be None")

        try:
            # Connect to the PostgreSQL database
            cur = self.conn.cursor()

            # Query to select records by telegram_id and target_wallet
            select_query = """
            SELECT * FROM monitor_wallets WHERE target_wallet = %s AND telegram_id = %s;
            """
            cur.execute(select_query, (wallet_address, telegram_id))

            # Get column names
            column_names = [desc[0] for desc in cur.description]

            result = cur.fetchall()
            if result is None:
                return []  # Return an empty list if no matching records found
            else:
                # Combine column names with data rows
                combined_result = [
                    (dict(zip(column_names, row)), row) for row in result if row
                ]
                return combined_result  # Return combined result
        except psycopg2.Error as e:
            print(
                f"The error occurred in get_monitor_wallet_by_telegram_id_token '{e}' "
            )
            self.conn.rollback()
            return []
        except AttributeError as e:
            print(f"AttributeError in get_monitor_wallet_by_telegram_id_token: {e}")
            return []
        except TypeError as e:
            print(f"TypeError in get_monitor_wallet_by_telegram_id_token: {e}")
            return []
        except ValueError as e:
            print(f"ValueError in get_monitor_wallet_by_telegram_id_token: {e}")
            return []
        except Exception as e:
            print(f"An error occurred in get_monitor_wallet_by_telegram_id_token: {e}")
            return []


if __name__ == "__main__":
    # db_manager = DatabaseManager()
    # db_manager.add_all_trade_data(1295934535, 'RPW17KwHtGepfzCuzQsabxGTyPKMUDNwpNuLpBgUM3b','aidenTrade',56,False,90,54,True)
    # db_manager.delete_all_monitor_wallets_data(1295934535, 9)
    # db_manager.get_wallet_records_with_column_names_for_telegram_id(1295934535, 11)
    # print(db_manager.get_wallet_encryped_key_by_telegram_id(1295934535))
    # db_manager.get_wallet_record_by_telegram_id_(1295934535)

    pass
