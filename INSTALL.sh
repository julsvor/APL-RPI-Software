#!/usr/bin/bash 
# set -e
cd "$(dirname "$0")"


if [ $(id -u) -ne 0 ]
  then echo Elevated permssions needed to use this script. Use sudo or root
  exit
fi

read -p "To start installation press any key" -n 1


SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run
BINARY_CLI_PROGRAM=tvi-dbcli
BINARY_GUI_PROGRAM=tvi-manager-gui

BINARY_SOURCE_DIR=./wrappers/
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

echo "Installing dependencies"
apt install -y mariadb-server libmariadb-dev python3-pyaudio python3-tk dos2unix

sudo dos2unix ./wrappers/*

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


echo "Copying wrappers from $BINARY_SOURCE_DIR to $BINARY_INSTALL_DIR"
cp ${BINARY_SOURCE_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM} $BINARY_INSTALL_DIR
chown tvi:tvi ${BINARY_INSTALL_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM}
chmod +x ${BINARY_INSTALL_DIR}{$BINARY_PROGRAM,$BINARY_CLI_PROGRAM,$BINARY_GUI_PROGRAM}


echo "Copying $SERVICE_FILE to $SERVICE_INSTALL_DIR"
cp $SERVICE_FILE $SERVICE_INSTALL_DIR
chown root "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"

echo "Setting up package in user '$SERVICE_USER'"
echo "Copying ./package to '/home/$SERVICE_USER'"
cp -r ./package /home/$SERVICE_USER/
chown -R tvi:tvi /home/$SERVICE_USER/package

echo "switching to user '$SERVICE_USER'"
su -s /bin/bash $SERVICE_USER -c "
  cd ~/
  echo 
  pipx install --force ./package
  rm -r ./package
  echo "exiting from user '$SERVICE_USER'"
"

echo "Installation finished, start the software with systemctl start tvi"
echo "Remember to create a new database with tvi-manager-gui or tvi-dbcli create"

