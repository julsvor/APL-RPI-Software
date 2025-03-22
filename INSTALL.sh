#!/usr/bin/bash 
# set -e

if [ $(id -u) -ne 0 ]
  then echo Elevated permssions needed to use this script. Use sudo or root
  exit
fi

read -p "To start installation press any key" -n 1

echo "Configuring virtual environment"
python3 -m venv /usr/local/lib/tvi
source /usr/local/lib/tvi/bin/activate

SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run
BINARY_CLI_PROGRAM=tvi-dbcli
BINARY_GUI_PROGRAM=tvi-manager-gui

BINARY_SOURCE_DIR=./wrappers/
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

LIBRARY_DIR=/usr/local/lib/tvi/lib/
LIB_PACKAGE=tvi_lib


echo "Installing dependencies"
apt install -y mariadb-server libmariadb-dev python3-pyaudio python3-tk
pip install mariadb

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

echo "Creating user '$SERVICE_USER' with group 'gpio'"
sudo groupadd gpio
sudo useradd -m -U -r -G gpio -s /usr/sbin/nologin $SERVICE_USER


echo "Copying executables from $BINARY_SOURCE_DIR to $BINARY_INSTALL_DIR"
cp ${BINARY_SOURCE_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM} $BINARY_INSTALL_DIR
chown tvi:tvi ${BINARY_INSTALL_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM}
chmod +x ${BINARY_INSTALL_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM}


echo "Copying $SERVICE_FILE to $SERVICE_INSTALL_DIR"
cp $SERVICE_FILE $SERVICE_INSTALL_DIR
chown root "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"


echo "Copying library files"
cp -r $LIB_PACKAGE $LIBRARY_DIR
chown -R tvi:tvi "${LIBRARY_DIR}${LIB_PACKAGE}"

cp -r ./bin/* /usr/local/lib/tvi
chown -R tvi:tvi /usr/local/lib/tvi

echo "Installation finished, start the software with systemctl start tvi"
echo "Remember to create a new database with tvi-manager-gui or tvi-dbcli create"

