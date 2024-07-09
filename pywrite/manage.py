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
    await client.__connect__()

    while True:
        user_input = input("Send a command to the client, or type /q to quit: ")
        if user_input == '/q':
            break
        else:
            response = await client.send(user_input)
            print(response)

    logger.info('Finished')

asyncio.run(main())