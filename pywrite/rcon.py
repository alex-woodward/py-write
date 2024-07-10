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

        self._active: bool = False
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self._cmd_queue: asyncio.Queue[list] = asyncio.Queue()
        self._process_task: asyncio.Task = None

    async def connect(self):
        # Begins connection process and deligates processing tasks.
        self._active = True
        if not self._process_task:
            self._process_task = asyncio.create_task(self._process())
            logger.info(f'Creating processing task: {self._process_task}.')

        logger.info(f'Initiating connection to {self.host}:{self.port}.')
        await self._reconnect()

    async def send(self, cmd):
        future = asyncio.Future()
        await self._cmd_queue.put((cmd, future))
        logger.debug(f'Queueing command "{cmd}" to {self.host}:{self.port}.')
        return await future
    
    async def _reconnect(self):
        attempt = 0
        while True:
            try:
                if not self._writer:
                    self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
                    await self._login()
                    break
            except (ConnectionError, OSError) as e:
                if attempt == 5:
                    self._cleanup(ConnectionError, "Unable to reconnect.")
                logger.error(f'Connection error: {e}. Retrying in 5 seconds...')
                attempt += 1
            await asyncio.sleep(5)

    async def _login(self):
        if await self._send(self.password, 3):
            logger.info(f'Successfully connected to {self.host}:{self.port}.')

    async def _read(self, len_b):
        data = b''
        while len(data) < len_b:
            data += await self._reader.read(len_b - len(data))
        return data

    async def _process(self):
        while self._active:
            try:
                command, future = await self._cmd_queue.get()
                result = await self._send(command)
                future.set_result(result)
                self._cmd_queue.task_done()
            
            # TODO: Graceful error handling.
            except asyncio.CancelledError:
                pass

            except ValueError as e:
                logger.error(f'RCON error: {e}')

            except (ConnectionError, OSError):
                logger.error(f'Connection lost. Attempting to reconnect...')
                await self._reconnect()

    async def _send(self, cmd: str, type=2):
        out_packet = struct.pack('<li', 0, type) + cmd.encode('utf8') + b'\x00\x00'
        out_len = struct.pack('<i', len(out_packet))
        self._writer.write(out_len + out_packet)
        logger.debug(f'Command "{cmd}" sent to {self.host}.')

        in_length = struct.unpack('<i', await self._read(4))
        in_packet = await self._read(in_length[0])

        logger.debug(f'Received response: {in_packet}')

        data = await self._verify(in_packet)
        
        return data.decode('utf8')

    async def _cleanup(self, err_type=None, err_val=None):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None
        self._active = False
        logger.info('Connection closed gracefully')

        if err_type:
            raise err_type(err_val)
    
    async def _verify(self, in_pkt):
        in_id, in_type = struct.unpack('<ii', in_pkt[:8])
        in_data, in_padd = in_pkt[8:-2], in_pkt[-2:]

        #if in_id != out_id:
        #    raise ValueError("Mismatched IDs")
        if in_id == -1:
            await self._cleanup(ValueError, "Incorrect password.")

        if in_padd != b'\x00\x00':
            await self._cleanup(ValueError, "Invalid padding.")

        return in_data 
