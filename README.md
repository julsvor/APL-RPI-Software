# Repository for raspberry pi phone to digital related software

## INSTALL
Run the script INSTALL.sh found in scripts/INSTALL.sh as sudo
```bash
sudo bash ./INSTALL.sh
```
The tvi-dbcli.py and tvi-run.py binaries will then be installed.
To run the program execute the command
```bash
sudo systemctl start tvi
```
To check status
```bash
sudo systemctl status tvi
```
To run at boot
```bash
sudo systemctl enable tvi
```
To then disable run at boot
```bash
sudo systemctl disable tvi
```
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
## Library files
### tvi_connection_utils.py
Contains code for network-audio interaction
### tvi_dbutils.py
Contains code for queries to database
### tvi_phone_pair.py
Contains code for a class that processes strings into proper ip and number pairs
### tvi_callmanager.py
Contains code for managing the state of the call aswell as some utility functions
## UNINSTALL
stop the program from running with the command
```bash
sudo systemctl stop tvi
```
Once you have made sure the program is not longer running then run the UNINSTALL script
```bash
sudo bash ./UNINSTALL.sh
```
