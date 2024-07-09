import asyncio
import os
import struct
import logging
logger = logging.getLogger(__name__)


class RconClient:
    def __init__(self, host=os.getenv("HOST"), port=os.getenv("PORT"), password=os.getenv("PASSWORD")):
        self.host = host
        self.port = port
        self.password = password

        self._active = False
        self._reader = None
        self._writer = None

    async def __connect__(self):
        logger.info(f'Initiating connection to {self.host}:{self.port}.')
        if not self._writer:  # Corrected the attribute name
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
            await self._login()
        
        return self

    async def _login(self):
        if not self._active and await self.send(self.password, 3):
            logger.info(f'Successfully connected to {self.host}:{self.port}.')
            self._active = True

    async def _read(self, len_b):
        data = b''
        while len(data) < len_b:
            data += await self._reader.read(len_b - len(data))  # Corrected the method name

        return data

    async def _send(self, type, cmd: str):
        logger.debug(f'Sending command: {cmd}')

        out_packet = struct.pack('<li', 0, type) + cmd.encode('utf8') + b'\x00\x00'
        out_len = struct.pack('<i', len(out_packet))
        self._writer.write(out_len + out_packet)

        in_length = struct.unpack('<i', await self._read(4))
        in_packet = await self._read(in_length[0])

        logger.debug(f'Received response: {in_packet}')

        data = verify(in_packet)
        
        
        return data.decode('utf8')
    
    async def _cleanup(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None
        self._active = False
        logger.info('Connection closed gracefully')

    async def send(self, cmd, packet_type=2):
        result = await self._send(packet_type, cmd)
        return result
    

def verify(in_pkt):
    in_id, in_type = struct.unpack('<ii', in_pkt[:8])
    in_data, in_padd = in_pkt[8:-2], in_pkt[-2:]

    #if in_id != out_id:
    #    raise ValueError("Mismatched IDs")
    if in_id == -1:
        raise ValueError("Incorrect password.")

    if in_padd != b'\x00\x00':
        raise ValueError("Invalid padding.")

    return in_data
