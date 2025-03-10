#!/bin/bash
# set -e

read -p "To start installation press any key" -n 1

SERVICE_USER=tvi

BINARY_PROGRAM=tvi-run.py
BINARY_INSTALL_DIR=/usr/local/bin/

SERVICE_FILE=tvi.service
SERVICE_INSTALL_DIR=/etc/systemd/system/

LIBRARY_DIR=/usr/local/lib/python3.11/dist-packages/
LIB1=tvi_connection_utils.py
LIB2=tvi_dbutils.py
LIB3=tvi_phone_ip_pair.py

echo "Creating user '$SERVICE_USER' with group 'gpio'"
sudo useradd -M -U -r -G gpio -s /usr/sbin/nologin $SERVICE_USER

echo "Copying $BINARY_PROGRAM to $BINARY_INSTALL_DIR"
cp $BINARY_PROGRAM $BINARY_INSTALL_DIR
chown tvi:tvi "${BINARY_INSTALL_DIR}${BINARY_PROGRAM}"

echo "Copying $SERVICE_FILE to $SERVICE_INSTALL_DIR"
cp $SERVICE_FILE $SERVICE_INSTALL_DIR
chown root "${SERVICE_INSTALL_DIR}${SERVICE_FILE}"

echo "Copying library packages"

cp $LIB1 $LIBRARY_DIR
chown tvi:tvi "${LIBRARY_DIR}${LIB1}"
cp $LIB2 $LIBRARY_DIR
chown tvi:tvi "${LIBRARY_DIR}${LIB2}"
cp $LIB3 $LIBRARY_DIR
chown tvi:tvi "${LIBRARY_DIR}${LIB3}"

echo "Installation finished, start the software with systemctl start tvi"

