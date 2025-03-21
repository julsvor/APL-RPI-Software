import threading, time, logging
from tvi_lib.tvi_callmanager import State, Command, CallManager

logger = logging.getLogger("tvi-logger")
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] - %(asctime)s - %(message)s", filename=None)



cm = CallManager()

##########
# Client #
##########
def call_ip(ip: str, port:int=5000) -> None:
    if cm.available_for_call() == True:
        logger.info(f"Calling IP {ip}")
        response = cm.client_request_call((ip, port))
        logger.info(f"Received response: {response}")
        if response == True:
            while True:
                audio_data = cm.read_audio_stream()
                cm.client_send_data((ip, port), Command.CONTINUE_CALL, audio_data)

                try:
                    data2, addr2 = cm.client_read_data()
                except TimeoutError as e:
                    logger.error("Client timed out waiting for response")
                    cm.set_state(State.IDLE)
                    break

##########
# Server #
##########
def listen_for_call():
    while True:
        raw_data, address = cm.server_read_data()
        command, _ = cm.parse_raw_data(raw_data)
        logger.debug(f"Server received command {Command(command)} from address {address}")
        if command == Command.START_CALL:
            cm.server_accept_call(address)
            while True:
                raw_data2, addr2 = cm.server_read_data()
                command, audio_data = cm.parse_raw_data(raw_data2)
                if addr2 != address:
                    logger.info("Rejecting interrupting incorrect address")
                    cm.server_reject_call(addr2)
                    continue

                cm.write_audio_stream(audio_data)
                cm.server_send_data(address, Command.CONTINUE_CALL, b"Server data")





server_thread = threading.Thread(target=listen_for_call)
server_thread.daemon = True
server_thread.start()

time.sleep(2)
call_ip("127.0.0.1")