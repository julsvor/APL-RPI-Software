import argparse
import sqlite3
import ipaddress

parser = argparse.ArgumentParser(prog='Phone DB CLI',description='create database or add/list/delete ip addresses in database')

parser.add_argument('action', help="[add, list, delete] adds or deletes an ip, list lists all ip addresses and their associated phone number") # get or add
parser.add_argument('-i', '--ip-addresses', action="append", help="add -i ip=phone_number -i another_ip=another_phone_number...| delete -i ip -i another_ip...") # Ip addresses to add or remove
parser.add_argument('-o', '--output', help="Where to output the database when create is used")
parser.add_argument('-db', '--database', help="Path to the database when list, delete or add is used")
parser.add_argument('-v', '--verbose', action='store_true')  # Verbose mode

number_size = 4 # Doesnt change the length of the number in the database creation query

def get_ips_from_db(db) -> list[str]:
    """Get all current IP addresses """
    con = sqlite3.connect(db)
    cursor = con.cursor()

    query = """
    SELECT phone_number, ip FROM phone_to_ip;
    """

    try:
        result = cursor.execute(query)
        index = 1
        records = result.fetchall()
        for record in records:
            print("Record %s: Number: '%s', IP Address: '%s'" % (index, record[0], ipaddress.ip_address(record[1])))
            index += 1
        if len(records) < 1:
            print("Database is empty")
    except sqlite3.OperationalError as e:
        print("[ERROR] %s" % e)
    finally:
        con.close()
    

def add_ips_to_db(db, ip_addresses:list[str]):
    con = sqlite3.connect(db)
    cursor = con.cursor()

    for ip_phone_combo in ip_addresses:
        if ip_phone_combo.count('=') != 1:
            print("[ERROR] Invalid IP and phone format %s" % ip_phone_combo)
            continue
        try:
            ip = ipaddress.ip_address(ip_phone_combo.split('=')[0])
        except ValueError as e:
            print("[ERROR] Invalid IP Adress: %s" % e)
            continue
        number = ip_phone_combo.split('=')[1]

        ## Check IP
        if ip.is_loopback:
            print("[WARNING] Added ip '%s' is a loopback address" % ip)
        
        ## Check Phone number
        if len(number) != number_size:
            print("[WARNING] Phone number '%s' is outside of the recommended size of %s digits" % (number_size, number))

        print("Adding ip '%s' with number '%s'" % (ip, number))

        query = """
        INSERT INTO phone_to_ip ('ip', 'phone_number')
        VALUES (?, ?);"""

        try:
            cursor.execute(query, (ip.packed, number))
            con.commit()
        except sqlite3.OperationalError as e:
            print("[ERROR] %s" % e)
        except sqlite3.IntegrityError as e:
            print("[ERROR] You can not have the same phone number pointing to different ip addresses. Error: %s" % e)
        finally:
            con.close()

def remove_ips_from_db(db, ip_addresses:list[str]):
    pass

def create_db(name):
    con = sqlite3.connect(name)
    cursor = con.cursor()

    query="""
    CREATE TABLE phone_to_ip(
    phone_number varchar(4) UNIQUE,
    ip BINARY(4)
    );
    """

    try:
        cursor.execute(query)
    except sqlite3.OperationalError as e:
        print("[ERROR] %s" % e)
    finally:
        con.close()



def main(args):
    database = "database.db"
    if args.database:
        database = args.database


    if args.action == "add":
        if args.ip_addresses == None:
            print("No ip addresses provided")
        else:
            add_ips_to_db(database, args.ip_addresses)
            
    elif args.action.lower() == "list":
        get_ips_from_db(database)
    elif args.action.lower() == "delete":
        remove_ips_from_db()
    elif args.action.lower() == "create":
        
        output_path = "database.db"
        if args.output:
            output_path = args.output
        create_db(output_path)
        if args.ip_addresses:
            add_ips_to_db(output_path, args.ip_addresses)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)