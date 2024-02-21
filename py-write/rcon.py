import asyncio
import os
import time
import struct

class RconClient:
    def __init__(self, host=os.getenv("HOST"), port=os.getenv("PORT"), password=os.getenv("PASSWORD")):
        self.host = host
        self.port = port
        self.password = password

        self._active = False
        self._reader = None
        self._writer = None

    async def __connect__(self):
        if not self._writer:  # Corrected the attribute name
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
            await self._login()
        
        return self

    async def _login(self):
        if not self._active and await self._send():
            self._active = True

    async def _read(self, len_b):
        data = b''
        while len(data) < len_b:
            data += await self._reader.read(len_b - len(data))  # Corrected the method name
        return data

    async def _send(self, type, cmd: str):
        out_id = struct.pack('<i', (time.time()/100))
        out_packet = out_id \
             + struct.pack('<i', type) + cmd.encode('utf8')
        
        self._writer.write(struct.pack('<i', len(out_packet) + out_packet + b'/x00/x00'))

        response = struct.unpack('<i', await self._read(4))
        in_packet = await self._read_data(response[0])

        data = verify(out_id, in_packet)  # Using data directly for further processing
        
        if not data:
            raise RuntimeError("Verification failed")  # Or any appropriate exception
        else:
            return data.decode('utf8')

    async def send(self, cmd):
        result = await self._send(2, cmd)
        return result
    

def verify(out_id, in_pkt):
    in_id, in_type = struct.unpack('<ii', in_pkt[:8])
    in_data, in_padd = in_pkt[8:-2], in_pkt[-2:]

    if in_id != out_id:
        raise ValueError("Mismatched IDs")  # Or any appropriate exception
    if in_type == -1:
        raise ValueError("Incorrect password")  # Or any appropriate exception
    if in_padd != b'/x00/x00':
        raise ValueError("Incorrect padding")  # Or any appropriate exception

    return in_data
