import logging, socket, pyaudio, threading
from enum import Enum
from pyaudio import PyAudio


logger = logging.getLogger("tvi-logger")


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
        quality = pyaudio.paInt16 # 2 Bytes per frame
        self.__command_length = 1 # 1 Byte
        self.__pyAudio = PyAudio()
        self.__audio_stream_input = self.__pyAudio.open(format=quality, frames_per_buffer=chunk_processing_size, channels=channels, rate=44100, input=True, output=False)
        self.__audio_stream_output = self.__pyAudio.open(format=quality, frames_per_buffer=chunk_processing_size, channels=channels, rate=44100, input=False, output=True)
        self.__chunk_size = chunk_processing_size
        self.__sock_buf_size = chunk_processing_size * 2 * channels + self.__command_length # For pyAudio16.
        self.__state = State.IDLE
        self.__server__socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
        self.__server__socket.bind(interface)
        self.__client_socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_DGRAM)
        self.__client_socket.settimeout(5)
        self.__interface = interface
        self.__state_lock = threading.Lock()
        self.__stream_lock = threading.Lock()

    # SHARED FUNCTIONS

    def parse_raw_data(self, data) -> tuple[Command, bytearray]:
        data = bytearray(data)
        command = data.pop(0)
        return Command(command), bytes(data)

    def read_audio_stream(self) -> bytes:
        with self.__stream_lock:
            data = self.__audio_stream_input.read(num_frames=self.__chunk_size, exception_on_overflow=True)
            return data

    def write_audio_stream(self, data) -> None:
        with self.__stream_lock:
            return self.__audio_stream_output.write(data)

    def get_state(self) -> State:
        with self.__state_lock:
            return self.__state

    def set_state(self, state: State) -> None:
        with self.__state_lock:
            self.__state = state

    def available_for_call(self) -> bool:
        with self.__state_lock:
            if self.__state == State.IDLE:
                return True
            return False
    

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

    def client_request_call(self, address) -> bool:
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

    def server_accept_call(self, address) -> bool:
        logger.debug(f"Accepting call from {address}")
        self.server_send_data(address, Command.ACCEPT_CALL)

    def server_reject_call(self, address):
        logger.debug(f"Rejecting call from {address}")
        self.server_send_data(address, Command.REJECT_CALL)

    def server_send_data(self, address, command:Command, data:bytes|None=None):

        packet: bytearray

        if data:
            packet = bytearray(command.value.to_bytes())
            packet.extend(data)
        else:
            packet = bytearray(command.value.to_bytes())

        self.__server__socket.sendto(packet, address)

    def server_read_data(self):
        data, addr = self.__server__socket.recvfrom(self.__sock_buf_size)
        return data, addr