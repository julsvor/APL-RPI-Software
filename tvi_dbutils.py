import argparse, sqlite3, logging, os, ipaddress
from tvi_phone_ip_pair import PhoneNumberIPPair

logger = logging.getLogger("TVI")

def get_ips_from_db(conn:sqlite3.Connection) -> list[str]|None:
    """Get all current records in database"""
    try:
        cursor = conn.cursor()

        query = """
        SELECT phone_number, ip FROM phone_to_ip;
        """

        result = cursor.execute(query)
        records = result.fetchall()
        return records
    except sqlite3.OperationalError as e:
        logger.error("SQLite error: ", exc_info=e)
    


def add_numbers_to_db(conn:sqlite3.Connection, ip_phone_combo:list[PhoneNumberIPPair]) -> None:
    try:
        cursor = conn.cursor()

        data_list = []

        for combo in ip_phone_combo:

            if combo.is_valid() == False:
                logger.error("Skipping, Invalid IP/Number format: '%s'" % combo.get_combo_str())
                continue

            data_list.append((combo.get_ip_address(), combo.get_phone_number()))

        query = """
        INSERT INTO phone_to_ip ('ip', 'phone_number')
        VALUES (?, ?);"""
            
        cursor.executemany(query, data_list)

        conn.commit()
    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)


def remove_numbers_from_db(conn:sqlite3.Connection, numbers_list:list[int], number_len):
    try:
        cursor = conn.cursor()

        data_list = []

        for number in numbers_list:

            if len(str(number)) != number_len:
                logger.error("Skipping, Number '%s' of length %i gotten, expected a number of length %i" % (number, len(str(number)), number_len))
                continue

            data_list.append(tuple([number]))

        query = """
        DELETE FROM phone_to_ip
        WHERE phone_number = ?;
        """
            
        cursor.executemany(query, data_list)

        conn.commit()
    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)


def create_db(name:str, meta_number_length) -> None:
    try:
        conn = sqlite3.connect(name)

        cursor = conn.cursor()

        cursor.execute("BEGIN TRANSACTION;")

        query="""
        CREATE TABLE phone_to_ip(
        phone_number INT(255) UNIQUE,
        ip BINARY(4)
        );
        """

        query2= """CREATE TABLE meta(
        phone_number_length INT NOT NULL UNIQUE
        );
        """

        query3 = """
        INSERT INTO meta ('phone_number_length') VALUES(?);
        """

        cursor.execute(query)
        cursor.execute(query2)
        cursor.execute(query3, tuple([meta_number_length]))

        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        logger.error("SQLite error: ", exc_info=e)
        os.remove(name)


def verify_database_structure(conn:sqlite3.Connection) -> bool:
    try:
        cursor = conn.cursor()

        query = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='phone_to_ip';
        """
        
        query2 = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='meta';
        """

        cursor.execute(query)
        resolve_table_exists = cursor.fetchone()

        cursor.execute(query2)
        meta_table_exists = cursor.fetchone()

        return False if not resolve_table_exists or not meta_table_exists else True
            

    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)
        return False


def get_database_number_len(conn:sqlite3.Connection) -> int | None:
    try:
        cursor = conn.cursor()

        query = """
        SELECT phone_number_length FROM meta;
        """

        cursor.execute(query)
        number_len = cursor.fetchone()

        return number_len[0] if type(number_len) == tuple else None
            

    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)



def resolve_number_to_ip(conn:sqlite3.Connection, number:int|str) -> str | None:
    logger.info("Attempting to resolve number '%s'" % number)
    try:
        cursor = conn.cursor()

        query = """
        SELECT ip FROM phone_to_ip WHERE phone_number = ?;
        """
        result = cursor.execute(query, (number,))
        result = result.fetchone()

        if type(result) == tuple:
            ip = str(ipaddress.ip_address(result[0]))
            logger.info("Resolved number '%s' to IP adress '%s'" % (number, ip))
            return ip
        return result
    except Exception as e:
        logger.error("Failed to resolve number '%s', got error:" % number, e, exc_info=True)


