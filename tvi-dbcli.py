#!/usr/bin/python

import os, sys

os.environ['PYTHONPATH'] = '/usr/local/lib/tvi/lib/python3.11/site-packages/'

sys.path = sys.path + [os.environ['PYTHONPATH']]


import argparse
import mariadb # type: ignore
import logging
from tvi_lib.tvi_phone_ip_pair import PhoneNumberIPPair
from tvi_lib.tvi_dbutils import create_db, add_numbers_to_db, remove_numbers_from_db, get_database_number_len, get_ips_from_db, drop_db, database_exists
from ipaddress import ip_address

logger = logging.getLogger("dbcli")
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(message)s")

# COMMAND PARSER
parser = argparse.ArgumentParser(
    prog=__package__,
    description='create databases and interact with data in them')
parser.add_argument('-v', '--verbose', action='store_true')

subparser = parser.add_subparsers(dest="command", required=True)

# Add to database
add_subparser = subparser.add_parser(
    "add", help="Add number/ip mappings to database")
add_subparser.add_argument(
    "ip_number_pairs",
    nargs='*',
    type=str,
    help="A list of numbers and their associated numbers to add")

# Delete from database
delete_subparser = subparser.add_parser(
    "delete", help="Remove numbers to database")
delete_subparser.add_argument(
    "numbers",
    nargs='*',
    type=str,
    help="A list of numbers to remove",
)

# List from database
list_subparser = subparser.add_parser(
    "list", help="List all records in database")

# Create a new database
create_subparser = subparser.add_parser("create", help="Initialize database")
create_subparser.add_argument(
    '-l',
    '--number-length',
    help="the length of numbers in the table",
    type=int,
    default=4,
    dest="number_length",
    required=False)

drop_subparser = subparser.add_parser("drop", help="Remove database")


def main(args):

    command = args.command
    db_exists = database_exists(user="tvi_dbcli_dbuser", password="readwrite")


    if command != "create":

        if db_exists == False:
            logger.critical("Database not found")
            exit(1)

        with mariadb.connect(host="localhost", user="tvi_dbcli_dbuser", password="readwrite", database="tvi") as conn:


            if command == "add":
                number_length = get_database_number_len(conn)
                ip_number_pairs = [PhoneNumberIPPair(combo,number_length) for combo in args.ip_number_pairs]

                if len(ip_number_pairs) < 1:
                    logger.info("No numbers to add")
                    exit(0)

                add_numbers_to_db(conn, ip_number_pairs)
            elif command == "list":
                number_length = get_database_number_len(conn)
                records = get_ips_from_db(conn)
                print(
                    "Databases phone_number length is set to: '%s'" %
                    number_length)
                if not records:
                    print("Database is empty")
                else:
                    for record in enumerate(records):
                        print(
                            "[record %s] %s = %s" %
                            (record[0], record[1][0], ip_address(
                                record[1][1]).compressed))
            elif command == "delete":
                numbers = args.numbers
                number_length = get_database_number_len(conn)
                if len(numbers) < 1:
                    logger.info("No numbers to delete")
                    exit(0)
                remove_numbers_from_db(conn, numbers, number_length)
            elif command == "drop":
                drop_db(conn)

    else:
        if db_exists == True:
            logger.critical("Database already exists")
            exit(1)

        create_db("tvi_dbcli_dbuser", "readwrite", args.number_length)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
