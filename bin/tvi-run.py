#!/usr/bin/python
import mariadb # type: ignore
import time, logging, ipaddress, os, threading
from gpiozero import InputDevice, OutputDevice  # type: ignore
from tvi_lib.tvi_dbutils import get_database_number_len, resolve_number_to_ip
from tvi_lib.tvi_connection_utils import call_ip, listen_for_call
from pathlib import Path

# LOGGING
logger = logging.getLogger("tvi-logger")
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] - %(asctime)s - %(message)s", filename=None)

# PIN SETUP
Dial = InputDevice(pin=5, pull_up=False)  # Start dialing
# Recieves pulse each falling edge when dialing is activated
Pulse = InputDevice(pin=6, pull_up=True) # Pulse

# CONFIG
timeout_len = 30  # Stores timeout in seconds between digits in a number, only checked when dialing is off

# GLOBAL VARS
db_connection = None  # Stores database connection
number_length: int  # Stores expected length of the number
number_arr = []  # Store whole number
timeout: int | None = None  # Stores last activated time when active
Dialing = 0  # Stores previous Dial value


# INIT
logger.info("Establishing connection to database")

db_connection = mariadb.connect(host="localhost", user="tvi_run_dbuser", password="", database="tvi") # Read only access

number_length = get_database_number_len(db_connection) # Get database number length to set expected number dialing length
logger.info(f"Setting number length to '{number_length}' as read from database")


logger.info("Listening for calls on interface 0.0.0.0:5000")
server_thread = threading.Thread(target=listen_for_call, daemon=True).start()

logger.info("Initialization finished")


# MAIN LOOP
while True:
    if Dialing != Dial.value:
        Dialing = Dial.value
        if Dialing == 1:
            logger.debug("Dialing started")
            digit = -1  # Negate first pulse
            last_pulse = Pulse.value # Track changes in pulse
            while Dial.value: # While dialing is active
                if last_pulse != Pulse.value:
                    if last_pulse == 1: # Add digit on rising edge of pulse
                        logger.debug(f"Recieved Pulse of value '{Pulse.value}'")
                        digit += 1
                last_pulse = Pulse.value
                time.sleep(0.01)
            # Dial is now off
            if digit >= 0 and digit <= 9:  # Number is between 0 and 9
                logger.debug(f"Digit '{digit}' recieved")
                logger.debug("Updating timeout")
                timeout = time.time()
                number_arr.append(digit)
                if len(number_arr) >= number_length: # Checks if a full number has been reached
                    number_str = "".join([str(number_digit) for number_digit in number_arr]) # Converts the number array to a string
                    logger.debug(f"Whole number '{number_str}' recieved")
                    number_arr.clear() 
                    timeout = None
                    logger.debug("Clearing timeout")
                    ip = resolve_number_to_ip(db_connection, number_str)
                    if ip: # resolve number to a valid ip address
                        logger.info(f"Successfully resolved number '{number_str}' to ip address '{ip}'")
                        call_ip(ip)
                    else:
                        logger.info(f"Resolving number '{number_str}' gave no results")     
            else:
                logger.error(f"Invalid digit '{digit}' recieved, skipping")
        elif Dialing == 0:
            logger.debug("Dialing stopped")


    if timeout is not None and time.time() >= timeout + timeout_len: # If timeout is enabled and has passed timeout length
        logger.info(f"Dialing has timed out after '{timeout_len}' seconds")
        timeout = None
        number_arr.clear()

    time.sleep(0.01)
