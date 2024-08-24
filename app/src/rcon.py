"""
rcon_client.py

This module provides an asynchronous RconClient class that manages connections to an RCON server,
sends commands, handles responses, and performs cleanup operations. The client supports automatic
reconnection and task management for processing commands.
"""

import asyncio
import os
import struct
import logging

logger = logging.getLogger(__name__)

class RconClient:
    """
    An asynchronous client for connecting to and interacting with an RCON server.

    The RconClient manages the connection, sends commands, processes responses, and handles 
    errors. It supports automatic reconnection and ensures that resources are cleaned up 
    gracefully on shutdown.

    Attributes:
        host (str): The RCON server hostname or IP address.
        port (int): The port number of the RCON server.
        password (str): The password used to authenticate with the RCON server.
        _active (bool): Indicates if the client is actively connected.
        _reader (asyncio.StreamReader): The stream reader for the connection.
        _writer (asyncio.StreamWriter): The stream writer for the connection.
        _cmd_queue (asyncio.Queue): The queue for commands to be sent to the server.
        _process_task (asyncio.Task): The task responsible for processing commands.
    """
    def __init__(self, host=os.getenv("HOST"), port=os.getenv("PORT"), password=os.getenv("PASSWORD")):
        """
        Initialize the RconClient with the server details and credentials.

        Args:
            host (str): The RCON server hostname or IP address.
            port (int): The port number of the RCON server.
            password (str): The password used to authenticate with the RCON server.
        """
        self.host = host
        self.port = port
        self.password = password

        self._active: bool = False
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self._cmd_queue: asyncio.Queue[list] = asyncio.Queue()
        self._process_task: asyncio.Task = None

    async def connect(self):
        """
        Initiates the connection to the RCON server and starts the command processing task.

        The method sets the active flag to True and creates an asynchronous task for processing 
        commands. It attempts to reconnect if the connection is not already established.
        """
        self._active = True
        if not self._process_task:
            self._process_task = asyncio.create_task(self._process())
            logger.info(f'Creating processing task: {self._process_task}.')

        logger.info(f'Initiating connection to {self.host}:{self.port}.')
        await self._reconnect()

    async def send(self, cmd):
        """
        Sends a command to the RCON server and returns the response.

        This method queues the command to be sent, waits for the response, and returns the result.

        Args:
            cmd (str): The command string to be sent to the server.

        Returns:
            str: The server's response to the command.
        """
        future = asyncio.Future()
        await self._cmd_queue.put((cmd, future))
        logger.debug(f'Queueing command "{cmd}" to {self.host}:{self.port}.')
        return await future

    async def cleanup(self, err_type=None, err_val=None):
        """
        Public method to gracefully close the connection and clean up resources.

        This method can be called by external managers to ensure that the connection 
        is properly closed and resources are released.

        Args:
            err_type (Exception, optional): The type of exception to raise after cleanup.
            err_val (str, optional): The error message associated with the exception.
        """
        await self._cleanup(err_type, err_val)

    async def _reconnect(self):
        """
        Attempts to reconnect to the RCON server.

        This method tries to establish a connection to the server, retrying up to 5 times if
        it fails. If the connection cannot be established after 5 attempts, it triggers cleanup.
        """
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
        """
        Authenticates with the RCON server using the provided password.

        This method sends the login command to the server and verifies the connection.
        Logs a message if the connection is successful.
        """
        if await self._send(self.password, 3):
            logger.info(f'Successfully connected to {self.host}:{self.port}.')

    async def _read(self, len_b):
        """
        Reads a specified number of bytes from the server.

        This method continues reading data until the specified length is reached.

        Args:
            len_b (int): The number of bytes to read from the stream.

        Returns:
            bytes: The data read from the server.
        """
        data = b''
        while len(data) < len_b:
            data += await self._reader.read(len_b - len(data))
        return data

    async def _process(self):
        """
        Processes commands from the command queue and sends them to the server.

        This method runs in a loop as long as the client is active, handling queued commands, 
        sending them to the server, and managing responses.
        """
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
        """
        Sends a command to the RCON server and waits for the response.

        This method constructs the command packet, sends it to the server, and reads the response.
        It also verifies the response packet to ensure it is valid.

        Args:
            cmd (str): The command string to send to the server.
            type (int, optional): The type of RCON packet to send. Defaults to 2.

        Returns:
            str: The decoded response data from the server.
        """
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
        """
        Private method to close the connection and clean up resources.

        This method ensures that the connection is properly closed, and any active tasks 
        are cancelled. It logs the closure and raises any specified errors.

        Args:
            err_type (Exception, optional): The type of exception to raise after cleanup.
            err_val (str, optional): The error message associated with the exception.
        """
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        if self._process_task:
            self._process_task.cancel()
        self._active = False
        logger.info('Connection closed gracefully')

        if err_type:
            raise err_type(err_val)

    async def _verify(self, in_pkt):
        """
        Verifies the response packet from the server.

        This method checks the packet ID, type, and padding to ensure it is valid.
        If the packet is invalid, it triggers cleanup and raises an appropriate error.

        Args:
            in_pkt (bytes): The response packet from the server.

        Returns:
            bytes: The data extracted from the packet.

        Raises:
            ValueError: If the packet is invalid or the ID is incorrect.
        """
        in_id, in_type = struct.unpack('<ii', in_pkt[:8])
        in_data, in_padd = in_pkt[8:-2], in_pkt[-2:]

        #if in_id != out_id:
        #    raise ValueError("Mismatched IDs")
        if in_id == -1:
            await self._cleanup(ValueError, "Incorrect password.")

        if in_padd != b'\x00\x00':
            await self._cleanup(ValueError, "Invalid padding.")

        return in_data 
