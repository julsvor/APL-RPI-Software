import logging
import ipaddress
import os
from tvi_lib.phone_ip_pair import PhoneNumberIPPair
import sqlite3

logger = logging.getLogger("tvi-logger-db")

def database_exists(db_name):
    if os.path.exists(db_name) and os.path.isfile(db_name):
        return True
    else:
        return False

def get_connection(db_name='tvi.db') -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    if not tables_exist(conn):
        create_tables(conn)
    return conn

def tables_exist(conn: sqlite3.Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='number_ip_mappings';")
    number_ip_exists = cursor.fetchone()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';")
    settings_exists = cursor.fetchone()
    return number_ip_exists is not None and settings_exists is not None

def create_tables(conn: sqlite3.Connection, number_length: int = 4) -> None:
    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS number_ip_mappings (
            number TEXT PRIMARY KEY,
            ip_address BLOB NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            number_length INTEGER NOT NULL
        );
        """)

        cursor.execute("SELECT COUNT(*) FROM settings;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO settings (number_length) VALUES (?);", (number_length,))
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)
        conn.rollback()


def get_ips_from_db(conn: sqlite3.Connection) -> list[str] | None:
    try:
        cursor = conn.cursor()

        query = """
        SELECT number, ip_address FROM number_ip_mappings;
        """

        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def add_numbers_to_db(conn: sqlite3.Connection, ip_phone_combo: list[PhoneNumberIPPair]) -> None:
    try:
        cursor = conn.cursor()

        data_list = []

        for combo in ip_phone_combo:

            if combo.is_valid() == False:
                logger.error("Skipping, Invalid IP/Number format: '%s'" % combo.get_combo_str(), exc_info=combo.get_error())
                continue

            data_list.append((combo.get_raw_ip_address(), combo.get_phone_number()))

        if len(data_list) < 1:
            logger.warning("No numbers were added as all failed to validate")
            return

        query = """
        INSERT INTO number_ip_mappings (ip_address, number)
        VALUES (?, ?);
        """

        cursor.executemany(query, data_list)

        conn.commit()
    except sqlite3.IntegrityError as e:
        logger.error("Trying to add number that already exists", exc_info=e)
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def remove_numbers_from_db(conn: sqlite3.Connection, numbers_list: list[str], number_length=4):
    try:
        cursor = conn.cursor()

        data_list = []

        for number in numbers_list:
            if len(number) != number_length:
                logger.error("Skipping, number '%s' of length '%s' gotten, expected number of length '%s'" % (number, len(number), number_length))
                continue
            logger.info("Adding number '%s' to delete list" % number)
            data_list.append((number,))

        if len(data_list) < 1:
            logger.warning("No numbers were removed as none were the correct format")
            return

        query = """
        DELETE FROM number_ip_mappings
        WHERE number = ?;
        """

        cursor.executemany(query, data_list)

        conn.commit()
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def get_database_number_len(conn: sqlite3.Connection) -> int | None:
    try:
        cursor = conn.cursor()

        query = """
        SELECT number_length FROM settings;
        """

        cursor.execute(query)
        number_len = cursor.fetchone()

        return number_len[0] if isinstance(number_len, tuple) else None

    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def resolve_number_to_ip(conn: sqlite3.Connection, number: int | str) -> str | None:
    logger.info("Attempting to resolve number '%s'" % number)
    try:
        cursor = conn.cursor()

        query = """
        SELECT ip_address FROM number_ip_mappings WHERE number = ?;
        """
        result = cursor.execute(query, (number,))
        result = cursor.fetchone()

        if isinstance(result, tuple):
            ip = str(ipaddress.ip_address(result[0]))
            logger.info("Resolved number '%s' to IP address '%s'" % (number, ip))
            return ip
        return result
    except Exception as e:
        logger.error(
            "Failed to resolve number '%s', got error:" %
            number, e, exc_info=True)


def drop_db(conn: sqlite3.Connection) -> None:
    try:
        cursor = conn.cursor()

        query = "DELETE FROM number_ip_mappings"

        cursor.execute(query)

        conn.commit()
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def add_record_to_db(conn: sqlite3.Connection, number: int, ip_address: str) -> None:
    try:
        cursor = conn.cursor()

        ip_address = ipaddress.ip_address(ip_address).packed

        query = """
        INSERT INTO number_ip_mappings (number, ip_address)
        VALUES (?, ?);
        """

        cursor.execute(query, (number, ip_address))

        conn.commit()
    except sqlite3.IntegrityError as e:
        logger.error("Trying to add number that already exists", exc_info=e)
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)


def remove_record_from_db(conn: sqlite3.Connection, number) -> None:
    try:
        cursor = conn.cursor()

        query = """
        DELETE FROM number_ip_mappings
        WHERE number = ?;
        """

        cursor.execute(query, (number,))

        conn.commit()
    except sqlite3.IntegrityError as e:
        logger.error("Trying to add number that already exists", exc_info=e)
    except sqlite3.Error as e:
        logger.error("SQLite3 error: ", exc_info=e)

