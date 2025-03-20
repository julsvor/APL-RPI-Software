from ipaddress import ip_address


class PhoneNumberIPPair():

    __phone_number: str
    __ip_address: bytes
    __is_valid: bool = True
    __error: Exception
    __combo_str: str
    __port: int = None

    def __init__(self, combo_str: str, phone_number_length=4):
        self.__combo_str = combo_str

        if combo_str.find(':') != -1:
            combo_str, port = combo_str.split(":", 1)

            port = int(port)
            self.__port = port


        number, ip = combo_str.split("=", 1)

        # IP VALIDATION
        ip = ip_address(ip)

        # NUMBER VALIDATION
        if num_len := len(number) != phone_number_length:
            raise ValueError("Incorrect number '%s' with length of '%s' gotten, expected number of length '%s'" % (number, num_len, phone_number_length))

        # ASSIGN VALUES
        self.__phone_number = number
        self.__ip_address = ip.packed

    def get_ip_address(self) -> str:
        ip = ip_address(self.__ip_address).compressed
        return ip

    def get_raw_ip_address(self) -> bytes:
        return bytes(self.__ip_address)

    def get_phone_number(self) -> str:
        return str(self.__phone_number)

    def get_error(self):
        return self.__error

    def get_combo_str(self):
        return self.__combo_str

    def is_valid(self) -> bool:
        return self.__is_valid
    
    def has_port(self) -> bool:
        return False if self.__port == None else True
    
    def get_port(self) -> int:
        return self.__port

