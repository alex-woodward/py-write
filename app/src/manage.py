import logging
import rcon
import asyncio
import sys


async def main():
    commands = sys.argv
    if '-l' in commands:
        logging.basicConfig(filename='pywrite.log', level=logging.DEBUG, 
            format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        logger.info('Started')

    client = rcon.RconClient('localhost', 25575, "1234")
    await client.connect()

    try:
        while True:
            user_input = input("Send a command to the client, or type /q to quit: ")
            if user_input == '/q':
                await client._cleanup()
                break
            else:
                response = await client.send(user_input)
                print(response)
    except asyncio.CancelledError:
        logger.error("Main coroutine cancelled.")

if __name__ == "__main__":
    asyncio.run(main())
