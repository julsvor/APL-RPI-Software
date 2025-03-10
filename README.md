# Repository for raspberry pi phone to digital related software
## tvi-run.py 
Main logic for reading signals and resolving numbers to ip addresses  
## tvi-dbcli 
Util functions and command line creation/interaction with sqlite database  
## Usage
On windows you may need to prefix dbcli with the python executable
```cmd
python.exe tvi-dbcli
```
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
List all records currenctly in the database along with the number length the database uses
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
