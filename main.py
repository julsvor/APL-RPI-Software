from gpiozero import InputDevice, OutputDevice
import sqlite3
import time
import logging
import ipaddress

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
# logger.disabled = True

Dial = InputDevice(pin=5, pull_up=False)
Pulse = InputDevice(pin=6, pull_up=True)

Dialing = 0

timeout_len = 30 # Timeout in seconds between digits in a number, only activates if dialing is off so states arent mismatched

number_length = 4 # Times out if not reached withing timeout_len, Stops dialing when reached

number_arr = []

timeout: int | None = None

def resolve_number_to_ip(number:str) -> str | None:
	logger.info("Resolving number: %s" % number)
	con = sqlite3.connect("database.db")
	cursor = con.cursor()

	query = """
	SELECT ip FROM phone_to_ip WHERE phone_number = ?;
	"""


	try:
		result = cursor.execute(query, (number,))
		result = result.fetchone()

		if type(result) == tuple:
			ip = str(ipaddress.ip_address(result[0]))
			logger.info("Resolved number '%s' to IP adress '%s'" % (number, ip))
			return ip
		return result
	except Exception as e:
		logger.error("Failed to resolve: %s", e, exc_info=True)

def CallIP(ip:str) -> None:
    pass

while True:
	if Dialing != Dial.value:
		Dialing = Dial.value
		if Dialing == 1:
			logger.debug("Dialing started")
			number = 0
			number -= 1 # Remove first pulse
			last_pulse = Pulse.value
			while Dial.value:
				if last_pulse != Pulse.value:
					if last_pulse == 1:
						logger.debug("Recieved Pulse")
						number += 1
				last_pulse = Pulse.value
				time.sleep(0.001)
			if number >= 0 and number <= 9:
				number_arr.append(number)
				if len(number_arr) >= number_length:
					number_str = "".join([str(digit) for digit in number_arr])
					logger.debug("Whole number recieved: %s" % number_str)
					ip = resolve_number_to_ip(number_str)
					number_arr.clear()
					timeout = None
			else:
				logger.error("Invalid digit recieved: %s" % number)

			logger.debug("Finished processing digit")
		elif Dialing == 0:
			timeout = time.time()
			logger.debug("Dialing stopped")

	if timeout != None and time.time() >= timeout + timeout_len:
		logger.info("Dialing has timed out after '%s' seconds" % timeout_len)
		timeout = None
		number_arr.clear()

	time.sleep(0.001)







