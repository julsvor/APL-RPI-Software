# Repository for raspberry pi phone to digital related software
## tvi-run.py 
Main logic for reading signals and resolving numbers to ip addresses

## INSTALL
Run the script INSTALL.sh as sudo
```bash
sudo bash ./INSTALL.sh
```
The tvi-dbcli.py and tvi-run.py binaries will then be installed.
An empty database with number length 4 will also be created.
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
## UNINStALL
stop the program from running with the command
```bash
sudo systemctl stop tvi
```
Once you have made sure the program is not longer running then run the UNINSTALL script
```bash
sudo bash ./UNINSTALL.sh
```
## tvi-dbcli 
Util functions and command line creation/interaction with sqlite database  
## Usage
You may need to prefix tvi-dbcli with the python executable
```bash
python tvi-dbcli
```
### add
Adds a record to the database
```bash
tvi-dbcli.py add 1234=192.168.50.4 # creates a record that points the number '1234' to the ip address '192.168.50.4'
```
### delete
Removes records belonging to the numbers provided
```bash
tvi-dbcli.py delete 1234 # Deletes all records associated with the number '1234'
```
### list
List all records currenctly in the database along with the number length the database uses
```bash
tvi-dbcli.py list # Lists all records
```
### create
Creates a new database with the proper structure and gives it the number length.
```bash
tvi-dbcli.py create # Creates a database new with the number length '4'
```
```bash
tvi-dbcli.py create -l 6 # Creates a database with the number length '6'
```
### drop
Drops the database and all records in it
```bash
tvi-dbcli.py drop # Drops the database and all records in it
```
