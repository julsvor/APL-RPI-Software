#!/bin/bash 

read -p "To start removal press any key" -n 1

if [ $(id -u) -ne 0 ]
  then echo Elevated permssions needed to use this script. Use sudo or root
  exit
fi


systemctl is-active --quiet tvi
if [ $? == 0 ]; then
echo "tvi service is still running, make sure its turned off before uninstalling"
exit
fi

# set -e

SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run
BINARY_CLI_PROGRAM=tvi-dbcli
BINARY_GUI_PROGRAM=tvi-manager-gui
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

LIBRARY_DIR=/usr/local/lib/tvi



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

echo "Removing programs at ${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"
rm ${BINARY_INSTALL_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM}

echo "Removing service at ${SERVICE_INSTALL_DIR}${SERVICE_FILE}"
rm "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"


echo "Removing libraries"

rm -r $LIBRARY_DIR

echo "Removal finished"

