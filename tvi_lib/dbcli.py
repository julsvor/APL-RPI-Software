#!/usr/bin/python
import os
import sys
import argparse
import logging
from tvi_lib.phone_ip_pair import PhoneNumberIPPair
from tvi_lib.dbutils import get_connection, add_numbers_to_db, remove_numbers_from_db, get_database_number_len, get_ips_from_db, drop_db, database_exists, create_tables
from ipaddress import ip_address

# Logger setup
logger = logging.getLogger("tvi-logger-dbcli")
logging.basicConfig(level=logging.WARNING, format="%(levelname)s - %(message)s")

# COMMAND PARSER SETUP
def setup_parser():
    parser = argparse.ArgumentParser(prog=__package__, description="Create databases and interact with data in them")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output")

    subparser = parser.add_subparsers(dest="command", required=True)

    # Add to database
    add_subparser = subparser.add_parser("add", help="Add number/ip mappings to database")
    add_subparser.add_argument("ip_number_pairs", nargs='*', type=str, help="A list of numbers and their associated numbers to add")

    # Delete from database
    delete_subparser = subparser.add_parser("delete", help="Remove numbers from database")
    delete_subparser.add_argument("numbers", nargs='*', type=str, help="A list of numbers to remove")

    # List records from database
    list_subparser = subparser.add_parser("list", help="List all records in database")

    # Create a new database
    create_subparser = subparser.add_parser("create", help="Initialize database")
    create_subparser.add_argument('-l', '--number-length', help="The length of numbers in the table", type=int, default=4, dest="number_length", required=False)

    # Drop the current database
    drop_subparser = subparser.add_parser("drop", help="Remove database")

    return parser

# COMMAND HANDLERS
def handle_add_command(args, db_conn):
    number_length = get_database_number_len(db_conn)
    ip_number_pairs = []

    for combo in args.ip_number_pairs:
        try:
            ip_number_pairs.append(PhoneNumberIPPair(combo, number_length))
        except Exception as e:
            logger.error("Failed to parse '%s'", combo, exc_info=e)

    if not ip_number_pairs:
        logger.info("No valid numbers to add")
        return

    add_numbers_to_db(db_conn, ip_number_pairs)

def handle_list_command(db_conn):
    number_length = get_database_number_len(db_conn)
    records = get_ips_from_db(db_conn)
    print(f"Database phone_number length is set to: '{number_length}'")
    if not records:
        print("Database is empty")
    else:
        for idx, record in enumerate(records):
            print(f"[record {idx}] {record[0]} = {ip_address(record[1]).compressed}")

def handle_delete_command(args, db_conn):
    numbers = args.numbers
    if not numbers:
        logger.info("No numbers to delete")
        return

    number_length = get_database_number_len(db_conn)
    remove_numbers_from_db(db_conn, numbers, number_length)

def handle_drop_command(db_conn):
    drop_db(db_conn)

def handle_create_command(args):
    if database_exists('tvi.db'):
        logger.critical("Database already exists")
        sys.exit(1)

    conn = get_connection('tvi.db')
    create_tables(conn, args.number_length)

# MAIN FUNCTION
def main():
    # Argument parsing
    parser = setup_parser()
    args = parser.parse_args()

    # Database existence check
    db_exists = database_exists("tvi.db")

    # Command-specific logic
    if args.command != "create":
        if not db_exists:
            logger.critical("Database not found")
            sys.exit(1)

        # Handle the specific database command
        with get_connection("tvi.db") as conn:
            if args.command == "add":
                handle_add_command(args, conn)
            elif args.command == "list":
                handle_list_command(conn)
            elif args.command == "delete":
                handle_delete_command(args, conn)
            elif args.command == "drop":
                handle_drop_command(conn)
    else:
        handle_create_command(args)

if __name__ == "__main__":
    main()
