import asyncio
import os
import time
import struct
from dotenv import load_dotenv

load_dotenv()

class RconClient:
    def __init__(self, host=os.getenv("HOST"), port=os.getenv("PORT"), password=os.getenv("PASSWORD")):
        self.host = host
        self.port = port
        self.password = password

        self._active = False
        self._reader = None
        self._writer = None

    async def __connect__(self):
        if not self.writer:
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
            await self._login()
        
        return self

    async def _login(self):
        if not self._active and await self._send():
            self._active = True

    async def _read(self, len_b):
        data = b''
        while len(data) < len_b:
            data += await self._reader(len_b, len(data))
        
        return data


    async def _send(self, type, cmd):
        packet = struct.pack('<i', (time.time()/100)) \
             + struct.pack('<i', type) + cmd
        
        self._writer.write(struct.pack('<i', len(packet) + packet + b'/x00/x00'))

        response = struct.unpack('<i', await self._read(4))
