import socket
from pyaudio import PyAudio
import pyaudio
from enum import Enum
import threading
import time
import logging

logger = logging.getLogger("tvi-logger")
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] - %(asctime)s - %(message)s", filename=None)

p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     print(p.get_device_info_by_index(i))

default_input_device = p.get_default_input_device_info()
print("Default Input Device:", default_input_device)

# Get default output device
default_output_device = p.get_default_output_device_info()
print("Default Output Device:", default_output_device)


exit(0)

class State(Enum):
    IDLE = 1
    CALLING = 2
    IN_CALL = 3


class Command(Enum):
    START_CALL = 4
    ACCEPT_CALL = 5
    REJECT_CALL = 6
    CONTINUE_CALL = 7
    END_CALL = 8


# Protocol command is of fixed length 1 byte
# Example 1data...

class CallManager:

    def __init__(self, chunk_processing_size=1024, interface=("0.0.0.0", 5000)):
        channels = 1 # Mono
        quality = pyaudio.paInt16
        self.__command_length = 1 # 1 Byte
        self.__pyAudio = PyAudio()
        self.__audio_stream = self.__pyAudio.open(format=quality, frames_per_buffer=chunk_processing_size, channels=channels, rate=44100, input=True, output=True)
        self.__chunk_size = chunk_processing_size
        self.__sock_buf_size = chunk_processing_size * 2 * channels + 1 # For pyAudio16. PyAduio8 = * 1, PyAduio16 = * 2, PyAduio32 = * 4 etc... With 1 channel
        self.__state = State.IDLE
        self.__server__socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
        self.__server__socket.bind(interface)
        self.__client_socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_DGRAM)
        self.__client_socket.settimeout(5)
        self.__interface = interface
        self.__state_lock = threading.Lock()
        self.__stream_lock = threading.Lock()

    # SHARED FUNCTIONS

    def read_audio_stream(self):
        with self.__stream_lock:
            data = self.__audio_stream.read(num_frames=self.__chunk_size)
            print("length of data", len(data))
            return data

    def write_audio_stream(self, data):
        with self.__stream_lock:
            return self.__audio_stream.write(data)

    def get_state(self):
        with self.__state_lock:
            return self.__state

    def set_state(self, state: State):
        with self.__state_lock:
            self.__state = state

    def available_for_call(self) -> bool:
        if self.__state == State.IDLE:
            return True
        return False
    
    def send_data(self, address, command:Command, data:bytes|None=None):

        packet: bytearray

        if data:
            packet = bytearray(command.value.to_bytes())
            packet.extend(data)
        else:
            packet = bytearray(command.value.to_bytes())

        self.__server__socket.sendto(packet, address)

    def read_data(self):
        data, addr = self.__server__socket.recvfrom(self.__sock_buf_size)
        return data, addr
    


    # CLIENT FUNCTIONS

    def client_send_data(self, address, command:Command, data:bytes|None=None):

        packet: bytearray

        if data:
            packet = bytearray(command.value.to_bytes())
            packet.extend(data)
        else:
            packet = bytearray(command.value.to_bytes())

        self.__client_socket.sendto(packet, address)

    def client_read_data(self) -> None|tuple:
            data, addr = self.__client_socket.recvfrom(self.__sock_buf_size)
            return data, addr

    def request_call(self, address) -> bool:
        logger.debug(f"Requesting call to {address}")
        self.set_state(State.CALLING)
        self.client_send_data(address, Command.START_CALL)
        try: 
            data, addr = self.client_read_data()

            if addr[0] == address[0] and data[0] == Command.ACCEPT_CALL.value:
                logger.debug(f"Server accepted call request with command {Command(data[0]).name}")
                return True
            
            if addr[0] == address[0] and data[0] == Command.REJECT_CALL.value:
                logger.error(f"Server rejected call request with command {Command(data[0]).name}")
                return False
            
            return False
        except TimeoutError as e:
            logger.error(f"Timed out requesting call to {address}")
            self.set_state(State.IDLE)
            return False

    # SERVER FUNCTIONS
    def accept_call(self, address) -> bool:
        logger.debug(f"Accepting call from {address}")
        self.send_data(address, Command.ACCEPT_CALL)

    def reject_call(self, address):
        logger.debug(f"Rejecting call from {address}")
        self.send_data(address, Command.REJECT_CALL)


cm = CallManager()

# Client
def call_ip(ip: str, port:int=5000) -> None:
    if cm.available_for_call() == True:
        logger.info(f"Calling IP {ip}")
        response = cm.request_call((ip, port))
        logger.info(f"Received response: {response}")
        if response == True:
            while True:
                logger.info("Sending data to server")
                audio_data = cm.read_audio_stream()
                cm.client_send_data((ip, port), Command.CONTINUE_CALL, audio_data)

                try:
                    data2, addr2 = cm.client_read_data()

                    logger.info(f"Recieved from server {data2}")
                except TimeoutError as e:
                    logger.error("Client timed out waiting for response")
                    cm.set_state(State.IDLE)
                # Process data, Play audio etc..

                time.sleep(1)

# Server
def listen_for_call():
    while True:
        data, addr = cm.read_data()
        # if cm.available_for_call() == True:
        command = data[0]
        logger.debug(f"Server recieved command {Command(command)} from address {addr}")
        if command == Command.START_CALL.value:
            cm.accept_call(addr)
            while True:
                data2, addr2 = cm.read_data()
                logger.info(f"Recieved from client {data2}")
                if addr2 != addr:
                    logger.info("Rejecting interrupting incorrect address")
                    cm.reject_call()
                    continue

                logger.info(f"Sending data to client {addr}")
                cm.send_data(addr, Command.CONTINUE_CALL, b"Server data")
        # else:
        #     cm.reject_call()




server_thread = threading.Thread(target=listen_for_call)
server_thread.daemon = True
server_thread.start()

client2_thread = threading.Thread(target=listen_for_call)

time.sleep(2)
call_ip("127.0.0.1")