"""
pywrite.py

This module provides command-line options for configuring logging in the pywrite application.
Users can specify logging to a file, output to the terminal, and set the logging verbosity level.
"""

import argparse
import logging

def parse_args():
    """
    Parse command-line arguments for the pywrite application.

    This function defines and parses the command-line arguments available to the user.
    It also configures logging based on the provided arguments.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Command-line options for pywrite.')

    parser.add_argument('-l', '--log-file',
                        action='store_true',
                        help='Enable logging to a file.')

    parser.add_argument('-s', '--stream-output',
                        action='store_true',
                        help='Enable logging to the terminal.')

    parser.add_argument('-v', '--verbosity',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set the logging level.')
    # Add more arguments as needed

    args = parser.parse_args()
    configure_logging(args)

    return args

def configure_logging(args):
    """
    Configure logging based on command-line arguments.

    This function sets up logging handlers and log levels based on the user's input.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    """
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
