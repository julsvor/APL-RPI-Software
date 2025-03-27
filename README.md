# Repository for raspberry pi phone to digital related software
## tvi-run.py 
Main logic for reading signals and resolving numbers to ip addresses
## tvi-manager-gui.py
A GUI for interacting with the associated database. It allows adding, listing and deletion of records in database. You can also create a new database with this tool.
## tvi-dbcli 
Util functions and command line creation/interaction with sqlite database  
## Usage
### add
Adds a record to the database
```bash
tvi-dbcli add 1234=192.168.50.4 # creates a record that points the number '1234' to the ip address '192.168.50.4'
```
### delete
Removes records belonging to the numbers provided
```bash
tvi-dbcli delete 1234 # Deletes all records associated with the number '1234'
```
### list
List all records currently in the database along with the number length the database uses
```bash
tvi-dbcli list # Lists all records
```
### create
Creates a new database with the proper structure and gives it the number length.
```bash
tvi-dbcli create # Creates a database new with the number length '4'
```
```bash
tvi-dbcli create -l 6 # Creates a database with the number length '6'
```
### drop
Drops the database and all records in it
```bash
tvi-dbcli drop # Drops the database and all records in it
```
## Library files
### tvi_connection_utils.py
Contains code for network-audio interaction
### tvi_dbutils.py
Contains code for interacting with the database
### tvi_phone_pair.py
Contains code for a class that processes strings into proper ip and number pairs. Useful for command-line input verification.
### tvi_callmanager.py
Contains code for managing the state of the call aswell as some utility functions
