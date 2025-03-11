#!/usr/bin/python
import mariadb
import time
import logging
import ipaddress
import os
from gpiozero import InputDevice, OutputDevice  # type: ignore
from tvi_dbutils import get_database_number_len, resolve_number_to_ip
from tvi_connection_utils import CallIP
from pathlib import Path


# LOGS_DIR = os.getenv("LOGS_DIRECTORY", None)
# logfile = "log.txt"

# if LOGS_DIR is not None:
#     LOGS_DIR = Path(LOGS_DIR, logfile)


# LOGGING
logger = logging.getLogger("tvi-logger")
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    filename=None)

# PIN SETUP
Dial = InputDevice(pin=5, pull_up=False)  # Start dialing
# Recieves pulse each falling edge when dialing is activated
Pulse = InputDevice(pin=6, pull_up=True)

# CONFIG
timeout_len = 30  # Stores timeout in seconds between digits in a number, only checked when dialing is off

# GLOBAL VARS
db_connection = None  # Stores database connection
number_length: int  # Stores expected length of the number
number_arr = []  # Store whole number
timeout: int | None = None  # Stores timeout timer
Dialing = 0  # Stores previous Dial value


# INIT
logger.info("Establishing connection to database")

db_connection = mariadb.connect(host="localhost", user="tvi_run_dbuser", password="", database="tvi") # Read only access

number_length = get_database_number_len(db_connection)
logger.info("Setting number length to '%i' as read from database" %
            number_length)


logger.info("Initialization finished")


# MAIN LOOP
while True:
    if Dialing != Dial.value:
        Dialing = Dial.value
        if Dialing == 1:
            logger.debug("Dialing started")
            digit = 0
            digit -= 1  # Remove first pulse
            last_pulse = Pulse.value
            while Dial.value:
                if last_pulse != Pulse.value:
                    if last_pulse == 1:
                        logger.debug("Recieved Pulse of value '%s'" % Pulse.value)
                        digit += 1
                last_pulse = Pulse.value
                time.sleep(0.01)
            # Dial is now off
            if digit >= 0 and digit <= 9:  # Number is between 0 and 9
                logger.debug("Digit '%i' recieved" % digit)
                logger.debug("Updating timeout")
                timeout = time.time()
                number_arr.append(digit)
                if len(number_arr) >= number_length:
                    number_str = "".join([str(digit) for digit in number_arr])
                    logger.debug("Whole number '%s' recieved" % number_str)
                    number_arr.clear()
                    logger.debug("Clearing timeout")
                    timeout = None
                    ip = resolve_number_to_ip(db_connection, number_str)
                    if ip:
                        logger.info(
                            "Successfully resolved number '%s' to ip address '%s'" % (number_str, ip))
                        # CallIP(ip)
                    else:
                        logger.info(
                            "Resolving number '%s' gave no results" % number_str)
                        
            else:
                logger.error("Invalid digit '%s' recieved, skipping" % digit)
        elif Dialing == 0:
            logger.debug("Dialing stopped")


    if timeout is not None and time.time() >= timeout + timeout_len:
        logger.info("Dialing has timed out after '%s' seconds" % timeout_len)
        timeout = None
        number_arr.clear()

    time.sleep(0.01)
