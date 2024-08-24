import asyncio
import logging
import rcon
from args import parse_args

async def main():
    # Parse command-line arguments
    parse_args()

    # Create and connect RCON client
    client = rcon.RconClient('localhost', 25575, "1234")
    await client.connect()

    try:
        while True:
            user_input = input("Send a command to the client, or type /q to quit: ")
            if user_input == '/q':
                await client._cleanup()
                break
            response = await client.send(user_input)

    except asyncio.CancelledError:
        # Log cancellation or handle cleanup if necessary
        logging.error("Main coroutine was cancelled.")

    finally:
        await client._cleanup()

if __name__ == "__main__":
    asyncio.run(main())
