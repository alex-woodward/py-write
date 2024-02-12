import socket
import os
import utils
import struct

class ServerSocket:
    def __init__(self):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        pass

    def receive(self):
        pass

def handshake(next_state: int) -> bytes:
    encoded_protocol = utils.encode_varint(os.getenv("PROTOCOL"))
    encoded_addr = utils.encode_string(os.getenv("ADDRESS"))
    encoded_port = struct.pack('>H', os.getenv("PORT"))
    encoded_state =  utils.encode_varint(next_state)
    