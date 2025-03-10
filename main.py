#!/usr/bin/python
import sqlite3, time, logging, ipaddress, os
from gpiozero import InputDevice, OutputDevice # type: ignore
from dbutil import verify_database_structure, get_database_number_len, resolve_number_to_ip
from connection_utils import CallIP

# LOGGING
logger = logging.getLogger("apl-rpi-software")
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] - %(asctime)s - %(message)s")

# PIN SETUP
Dial = InputDevice(pin=5, pull_up=False) # Start dialing
Pulse = InputDevice(pin=6, pull_up=True) # Recieves pulse each falling edge when dialing is activated

# CONFIG
database_name = "database.db" # Stores the name of the database file
timeout_len = 30 # Stores timeout in seconds between digits in a number, only checked when dialing is off

# GLOBAL VARS
db_connection = None # Stores database connection
number_length:int # Stores expected length of the number
number_arr = [] # Store whole number
timeout: int | None = None # Stores timeout timer
Dialing = 0 # Stores previous Dial value



## INIT
if not os.path.isfile(database_name):
	logger.critical("Database '%s' not found" % database_name)
	exit(1)

with sqlite3.connect(database_name) as conn:

	logger.info("Establishing connection to database '%s'" % database_name)
	db_connection = conn

	if verify_database_structure(db_connection) == False:
		logger.critical("Database doesnt the correct structure")
		exit(1)


	number_length = get_database_number_len(conn)
	logger.info("Setting number length to '%i' as read from database" % number_length)


	logger.info("Initialization finished")



while True:
	if Dialing != Dial.value:
		Dialing = Dial.value
		if Dialing == 1:
			logger.debug("Dialing started")
			digit = 0
			digit -= 1 # Remove first pulse
			last_pulse = Pulse.value
			while Dial.value:
				if last_pulse != Pulse.value:
					if last_pulse == 1:
						logger.debug("Recieved Pulse")
						digit += 1
				last_pulse = Pulse.value
				time.sleep(0.001)
			if digit >= 0 and digit <= 9: # Number is between 0 and 9
				logger.debug("Digit '%i' recieved" % digit)
				number_arr.append(digit)
				if len(number_arr) >= number_length:
					number_str = "".join([str(digit) for digit in number_arr])
					logger.debug("Whole number '%s' recieved" % number_str)
					ip = resolve_number_to_ip(db_connection, number_str)
					if ip:
						logger.info("Successfully resolved number '%s' to ip address '%s'" % (number_str, ip))
						# CallIP(ip)
					else:
						logger.info("Resolving number '%s' gave no results" % number_str)

					number_arr.clear()
					timeout = None
			else:
				logger.error("Invalid digit '%s' recieved, skipping" % digit)
		elif Dialing == 0:
			timeout = time.time()
			logger.debug("Dialing stopped")


	if timeout != None and time.time() >= timeout + timeout_len:
		logger.info("Dialing has timed out after '%s' seconds" % timeout_len)
		timeout = None
		number_arr.clear()

	time.sleep(0.001)



