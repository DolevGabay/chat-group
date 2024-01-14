# logging_config.py

import logging

def configure_logging():
    # Logging configuration
    LOG_FILE = 'server.log'
    LOG_LEVEL = logging.INFO

    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    logging.getLogger().addHandler(console_handler)
