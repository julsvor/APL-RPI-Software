import argparse
import logging
import os
import ipaddress
import mariadb
from tvi_phone_ip_pair import PhoneNumberIPPair

logger = logging.getLogger("tvi-logger")


def get_ips_from_db(conn: mariadb.Connection) -> list[str] | None:
    try:
        cursor = conn.cursor()

        query = """
        SELECT number, ip_address FROM number_ip_mappings;
        """

        result = cursor.execute(query)
        records = cursor.fetchall()
        return records
    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)


def add_numbers_to_db(conn: mariadb.Connection,
                      ip_phone_combo: list[PhoneNumberIPPair]) -> None:
    try:
        cursor = conn.cursor()

        data_list = []

        for combo in ip_phone_combo:

            if combo.is_valid() == False:
                logger.error(
                    "Skipping, Invalid IP/Number format: '%s'" %
                    combo.get_combo_str(),
                    exc_info=combo.get_error())
                continue

            data_list.append(
                (combo.get_raw_ip_address(),
                 combo.get_phone_number()))

        if len(data_list) < 1:
            logger.warning("No numbers were added as all failed to validate")
            return

        query = """
        INSERT INTO number_ip_mappings (ip_address, number)
        VALUES (?, ?);"""

        cursor.executemany(query, data_list)

        conn.commit()
    except mariadb.IntegrityError as e:
        logger.error("Trying to add number that already exists")
    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)


def remove_numbers_from_db(conn: mariadb.Connection, numbers_list: list[int]):
    try:
        cursor = conn.cursor()

        data_list = []

        for number in numbers_list:
            data_list.append(tuple([number]))

        query = """
        DELETE FROM number_ip_mappings
        WHERE number = ?;
        """

        cursor.executemany(query, data_list)

        conn.commit()
    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)


def get_database_number_len(conn: mariadb.Connection) -> int | None:
    try:
        cursor = conn.cursor()

        query = """
        SELECT number_length FROM settings;
        """

        cursor.execute(query)
        number_len = cursor.fetchone()

        return number_len[0] if isinstance(number_len, tuple) else None

    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)


def resolve_number_to_ip(conn: mariadb.Connection,
                         number: int | str) -> str | None:
    logger.info("Attempting to resolve number '%s'" % number)
    try:
        cursor = conn.cursor()

        query = """
        SELECT ip FROM number_ip_mappings WHERE number = ?;
        """
        result = cursor.execute(query, (number,))
        result = cursor.fetchone()

        if isinstance(result, tuple):
            ip = str(ipaddress.ip_address(result[0]))
            logger.info(
                "Resolved number '%s' to IP adress '%s'" %
                (number, ip))
            return ip
        return result
    except Exception as e:
        logger.error(
            "Failed to resolve number '%s', got error:" %
            number, e, exc_info=True)


def create_db(user: str, password: str, number_length: int) -> None:
    try:
        conn = mariadb.connect(host="localhost", user=user, password=password)

        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE tvi")

        cursor.execute("USE tvi")

        cursor.execute("START TRANSACTION;")

        query = """
            CREATE TABLE IF NOT EXISTS number_ip_mappings (
                number INT UNSIGNED PRIMARY KEY,
                ip_address BINARY(4) NOT NULL,
                port INT UNSIGNED NULL,
                UNIQUE (number),
                INDEX (ip_address)
            );
        """

        query2 = """
            CREATE TABLE IF NOT EXISTS settings (
                id TINYINT UNSIGNED PRIMARY KEY DEFAULT 1,
                number_length TINYINT UNSIGNED NOT NULL,
                CONSTRAINT unique_settings CHECK (id = 1)
            );
        """

        query3 = """
            INSERT INTO settings (number_length) VALUES(?);
        """

        cursor.execute(query)
        cursor.execute(query2)
        cursor.execute(query3, tuple([number_length]))

        conn.commit()
    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)


def drop_db(conn: mariadb.Connection) -> None:
    try:

        cursor = conn.cursor()

        query = "DROP DATABASE tvi;"

        cursor.execute(query)

        conn.commit()
    except mariadb.Error as e:
        logger.error("MariaDB error: ", exc_info=e)
