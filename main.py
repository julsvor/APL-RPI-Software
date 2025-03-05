from gpiozero import InputDevice, OutputDevice
import sqlite3

# Pulse = InputDevice(2) # Pin 2, Active when dialing starts and inactiv when it isnt
# Dialing = InputDevice(3) # Pin 3, Pulses everytime it passes a number



# When dialing starts Pulse can be accepted
# Pulse is changed when dialing reached a new
#
#
#
#
#
#




# Prototyping

### Gets
def resolve_number_to_ip(number):
    con = sqlite3.connect("database.db")
    cursor = con.cursor()

    query = """
    SELECT phone_number FROM phone_to_ip WHERE phone_number = ?;
    """

    result = cursor.execute(query, (number,))
    result = result.fetchone()

    if type(result) == tuple:
        return result[0]

    return result

def CallIP():
    pass


x = resolve_number_to_ip("4330")
print(x)







