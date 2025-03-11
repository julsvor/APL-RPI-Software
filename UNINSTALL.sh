#!/usr/bin/bash
# set -e

read -p "To start removal press any key" -n 1

# To make sure the service isnt running
sudo systemctl stop tvi

SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run.py
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

LIBRARY_DIR=/usr/local/lib/tvi/lib/python3.11/site-packages/
LIB1=tvi_connection_utils.py
LIB2=tvi_dbutils.py
LIB3=tvi_phone_ip_pair.py


echo "Dropping database and users"

mariadb -e "
DROP DATABASE tvi;
"

mariadb -e "
DROP USER 'tvi_run_dbuser'@localhost;
"

mariadb -e "
DROP USER 'tvi_dbcli_dbuser'@localhost; 
"


echo "Removing user '$SERVICE_USER'"
userdel $SERVICE_USER

echo "Removing program at ${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"
rm "${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"

echo "Removing service at ${SERVICE_INSTALL_DIR}${SERVICE_FILE}"
rm "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"


echo "Removing libraries"

rm "${LIBRARY_DIR}${LIB1}"
rm "${LIBRARY_DIR}${LIB2}"
rm "${LIBRARY_DIR}${LIB3}"

rm -r "/usr/local/lib/tvi"

echo "Removal finished"

