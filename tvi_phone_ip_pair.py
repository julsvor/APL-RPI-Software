from ipaddress import ip_address

class PhoneNumberIPPair():

    __phone_number:int
    __ip_address:bytes
    __is_valid:bool = True
    __error:Exception
    __combo_str:str
    __port: int

    def __init__(self, combo_str:str, phone_number_size=4):
        self.__combo_str = combo_str
        try:

            combo_str, port = combo_str.split(":", 1)

            if port and type(port) == int:
                self.__port = port
                raise NotImplementedError("Port feature has not been implmented yet")

            number, ip = combo_str.split("=", 1)


            ## IP VALIDATION
            ip = ip_address(ip)

            ## NUMBER VALIDATION
            if len(number) != phone_number_size:
                raise ValueError("Incorrect number size")

            ## ASSIGN VALUES
            self.__phone_number = int(number)
            self.__ip_address = ip.packed


        except Exception as e:
            self.__is_valid = False
            self.__error = e

    def get_ip_address(self) -> str:
        ip = [str(x) for x in self.__ip_address]
        ip = ".".join(ip)
        return ip
        
    
    def get_phone_number(self) -> str:
        return self.__phone_number

    def get_error(self):
        return self.__error

    def get_combo_str(self):
        return self.__combo_str

    def is_valid(self) -> bool:
        return self.__is_valid

    def __str__(self):
        return self.__combo_str

    def __repr__(self):
        return f"PhoneNumberIPPair(ip='{self.get_ip_address()}', number='{self.get_phone_number()}')"

