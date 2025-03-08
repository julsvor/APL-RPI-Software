import argparse, sqlite3, logging, os
from phone_ip_pair import PhoneNumberIPPair


logger = logging.getLogger()
logging.basicConfig(level=logging.WARNING, format="%(levelname)s - %(message)s")

## COMMAND PARSER
parser = argparse.ArgumentParser(prog='dbcli',description='create database and interact with ip addresses in database')
parser.add_argument('-v', '--verbose', action='store_true')

subparser = parser.add_subparsers(dest="command")

## Add to database
add_subparser = subparser.add_parser("add")
add_subparser.add_argument("ip_number_pairs", nargs='*', type=str, help="A list of numbers and their associated ip addresses to add")
add_subparser.add_argument('-db', '--database', help="path to the database to use", default="database.db", type=str)

## Delete from database
delete_subparser = subparser.add_parser("delete")
delete_subparser.add_argument("numbers", nargs='*', type=int, help="A list of numbers to remove",)
delete_subparser.add_argument('-db', '--database', help="path to the database to use", default="database.db", type=str)

## List from database
list_subparser = subparser.add_parser("list")
list_subparser.add_argument('-db', '--database', help="path to the database to use", default="database.db", type=str)

## Create a new database
create_subparser = subparser.add_parser("create")
create_subparser.add_argument('-n', '--name', help="name of the database to create", type=str, default='database.db', dest="database", required=False)
create_subparser.add_argument('-l', '--number-length', help="the length of numbers in the table", type=int, default=4, dest="number_length", required=False)

## Verify database structure
validate_subparser = subparser.add_parser("validate")
validate_subparser.add_argument('-db', '--database', help="path to the database to use", default="database.db", type=str)


def get_ips_from_db(db) -> list[str]|None:
    """Get all current IP addresses """
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            query = """
            SELECT phone_number, ip FROM phone_to_ip;
            """

            result = cursor.execute(query)
            records = result.fetchall()
            return records
    except sqlite3.OperationalError as e:
        logger.error("SQLite error: ", exc_info=e)
    


def add_numbers_to_db(db, ip_phone_combo:list[PhoneNumberIPPair]) -> None:
    try:
        with sqlite3.connect(db) as conn:
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


def remove_numbers_from_db(db, numbers_list:list[int], number_len):
    try:
        with sqlite3.connect(db) as conn:
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


def create_db(name, meta_number_length) -> None:
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


def verify_database_structure(name) -> bool:
    try:
        with sqlite3.connect(name) as conn:
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

            return False if not resolve_table_exists and meta_table_exists else True
            

    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)


def get_database_number_len(name) -> int | None:
    try:
        with sqlite3.connect(name) as conn:
            cursor = conn.cursor()

            query = """
            SELECT phone_number_length FROM meta;
            """

            cursor.execute(query)
            number_len = cursor.fetchone()

            return number_len[0] if type(number_len) == tuple else None
            

    except sqlite3.Error as e:
        logger.error("SQLite error: ", exc_info=e)


def main(args):

    command = args.command
    database = args.database


    if command == "create":
        output_path = database
        
        if os.path.isfile(database) == True:
            logger.critical("Database file '%s' already exists", database)
            exit(1)

        create_db(output_path, args.number_length)
    else:

        if os.path.isfile(database) == False:
            logger.critical("Database file '%s' not found", database)
            exit(1)

        if verify_database_structure(database) == False:
            logger.critical("Invalid database structure")
            exit(1)
        

        if command == "add":
            number_length = get_database_number_len(database)
            ip_number_pairs = [PhoneNumberIPPair(combo, number_length) for combo in args.ip_number_pairs]
            add_numbers_to_db(database, ip_number_pairs)
        elif command == "list":
            number_length = get_database_number_len(database)
            records = get_ips_from_db(database)
            print("Databases phone_number length is set to: '%s'" % number_length)
            if not records:
                print("Database is empty")
            else:
                for record in enumerate(records):
                    print("[record %s] %s = %s" % (record[0], record[1][0], record[1][1]))
        elif command == "delete":
            number_length = get_database_number_len(database)
            numbers = args.numbers
            remove_numbers_from_db(database, numbers, number_length)
        elif command == "validate":
            valid = verify_database_structure(database)
            if valid:
                print("Database is valid")
            else:
                print("Database is not valid")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)