"""
manage.py

This script provides a command-line interface for interacting with an RCON server using the
RconClient class. It parses command-line arguments, establishes a connection to the server, 
and allows the user to send commands interactively.

The script also handles graceful shutdown and cleanup when the user quits or the process is 
interrupted.
"""

import asyncio
import logging
import rcon
from args import parse_args

async def main():
    """
    The main coroutine that runs the RCON client interaction loop.

    This function parses command-line arguments, initializes the RconClient, and connects 
    to the RCON server. It enters an interactive loop where the user can send commands 
    to the server or type '/q' to quit. The function handles cleanup and error logging 
    on cancellation or shutdown.
    """
    # Parse command-line arguments
    parse_args()

    # Create and connect RCON client
    client = rcon.RconClient('localhost', 25575, "1234")
    await client.connect()

    try:
        while True:
            user_input = input("Send a command to the client, or type /q to quit: ")
            if user_input == '/q':
                await client.close()
                break
            response = await client.send(user_input)
            print(response)

    except asyncio.CancelledError:
        # Log cancellation or handle cleanup if necessary
        logging.error("Main coroutine was cancelled.")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
