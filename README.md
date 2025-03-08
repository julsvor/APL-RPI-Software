# Repository for raspberry pi phone to digital related software
## main.py 
Main logic for reading analog signals and resolving numbers to ip addresses  
  
  
## phone_db_cli 
Util functions and command line creation/interaction with sqlite database  
## Usage
On windows you may need to prefix dbcli with the python executable
```cmd
python.exe dbcli
```
### add
Adds a record to the database
```bash
dbcli add 1234=192.168.50.4 # creates a record that points the number '1234' to the ip address '192.168.50.4'
```
You can also select which database used
```bash
dbcli add -db example.db 1234=192.168.50.4 # Uses the database 'example.db'
```
### delete
Removes records belonging to the numbers provided
```bash
dbcli delete 1234 # Deletes all records associated with the number '1234'
```
```bash
dbcli delete -db example.db 1234 # Deletes all records associated with the number '1234' # Uses the database 'example.db'
```
### list
List all records currenctly in the database along with the number length the database uses
```bash
dbcli list # Lists all records
```
```bash
dbcli list -db example.db # Reads from the database 'example.db'
```
### create
Creates a new database with the proper structure and gives it the number length.
```bash
dbcli create # Creates a database named 'database.db' with the number length '4'
```
```bash
dbcli create -n example.db -l 6 # Creates a database named 'example.db' with the number length '6'
```
### validate
validates a databases table structure
```bash