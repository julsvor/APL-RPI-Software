#!/usr/bin/python
import argparse, sqlite3, logging, os
from phone_ip_pair import PhoneNumberIPPair
from dbutil import create_db, add_numbers_to_db, remove_numbers_from_db, get_database_number_len, get_ips_from_db, verify_database_structure

logger = logging.getLogger("dbcli")
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



def main(args):

    command = args.command
    database = args.database



    if command != "create":
            if os.path.isfile(database) == False:
                logger.critical("Database file '%s' not found", database)
                exit(1)

            if verify_database_structure(database) == False:
                logger.critical("Invalid database structure")
                exit(1)

            with sqlite3.connect(database) as conn:
                if command == "add":
                    number_length = get_database_number_len(conn)
                    ip_number_pairs = [PhoneNumberIPPair(combo, number_length) for combo in args.ip_number_pairs]
                    add_numbers_to_db(conn, ip_number_pairs)
                elif command == "list":
                    number_length = get_database_number_len(conn)
                    records = get_ips_from_db(conn)
                    print("Databases phone_number length is set to: '%s'" % number_length)
                    if not records:
                        print("Database is empty")
                    else:
                        for record in enumerate(records):
                            print("[record %s] %s = %s" % (record[0], record[1][0], record[1][1]))
                elif command == "delete":
                    number_length = get_database_number_len(conn)
                    numbers = args.numbers
                    remove_numbers_from_db(conn, numbers, number_length)
                elif command == "validate":
                    valid = verify_database_structure(conn)
                    if valid:
                        print("Database is valid")
                    else:
                        print("Database is not valid")

        
    else:
        if os.path.isfile(database) == True:
            logger.critical("Database file '%s' already exists", database)
            exit(1)

        create_db(database, args.number_length)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)