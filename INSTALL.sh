#!/usr/bin/bash
set -e

if [ $(id -u) -ne 0 ]
  then echo Elevated permssions needed to use this script. Use sudo or root
  exit
fi

read -p "To start installation press any key" -n 1

SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run.py
BINARY_CLI_PROGRAM=tvi-dbcli.py
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

LIBRARY_DIR=/usr/local/lib/tvi/lib/python3.11/site-packages/
LIB_PACKAGE=tvi_lib

echo "Installing MariaDB"
apt install -y mariadb-server libmariadb-dev

mariadb -e "
CREATE USER 'tvi_run_dbuser'@localhost IDENTIFIED BY '';
GRANT SELECT ON *.* TO 'tvi_run_dbuser'@'localhost';
FLUSH PRIVILEGES;
"

mariadb -e "
CREATE USER 'tvi_dbcli_dbuser'@localhost IDENTIFIED BY 'readwrite'; 
GRANT ALL PRIVILEGES ON *.* TO 'tvi_dbcli_dbuser'@'localhost';
FLUSH PRIVILEGES;
"

python3 -m venv /usr/local/lib/tvi
source /usr/local/lib/tvi/bin/activate
pip install mariadb

PYTHONPATH=/usr/local/lib/tvi/lib/python3.11/site-packages/ /usr/bin/python ./$BINARY_CLI_PROGRAM create

echo "Creating user '$SERVICE_USER' with group 'gpio'"
sudo useradd -m -U -r -G gpio -s /usr/sbin/nologin $SERVICE_USER

echo "Copying $BINARY_PROGRAM to $BINARY_INSTALL_DIR"
cp $BINARY_PROGRAM $BINARY_INSTALL_DIR
chown tvi:tvi "${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"
chmod +x "${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"

echo "Copying $BINARY_CLI_PROGRAM to $BINARY_INSTALL_DIR"
cp $BINARY_CLI_PROGRAM $BINARY_INSTALL_DIR
chown tvi:tvi "${BINARY_INSTALL_DIR}${BINARY_CLI_PROGRAM}"
chmod +x "${BINARY_INSTALL_DIR}${BINARY_CLI_PROGRAM}"

echo "Copying $SERVICE_FILE to $SERVICE_INSTALL_DIR"
cp $SERVICE_FILE $SERVICE_INSTALL_DIR
chown root "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"

echo "Copying library packages"

cp -r $LIB_PACKAGE $LIBRARY_DIR
chown -r tvi:tvi "${LIBRARY_DIR}${$LIB_PACKAGE}"


echo "Installation finished, start the software with systemctl start tvi"


