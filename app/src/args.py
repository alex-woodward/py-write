import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(description='Command-line options for pywrite.')
    
    parser.add_argument('-l', '--log-file', action='store_true', help='Enable logging to a file.')
    parser.add_argument('-s', '--stream-output', action='store_true', help='Enable logging to the terminal.')
    parser.add_argument('-v', '--verbosity', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level.')
    # Add more arguments as needed
    
    args = parser.parse_args()
    configure_logging(args)
    
    return args

def configure_logging(args):
    handlers = []

    if args.log_file:
        file_handler = logging.FileHandler('pywrite.log')
        handlers.append(file_handler)

    if args.stream_output:
        console_handler = logging.StreamHandler()
        handlers.append(console_handler)

    # Set the logging level
    log_level = getattr(logging, args.verbosity.upper(), logging.INFO)
    logging.basicConfig(level=log_level, 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        handlers=handlers)

    logger = logging.getLogger(__name__)
    logger.info('Logging configured.')