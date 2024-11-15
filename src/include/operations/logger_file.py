# logging_config.py
import logging
from io import StringIO

# Set up the log stream and logger
log_stream = StringIO()

def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create and configure the in-memory handler
    memory_handler = logging.StreamHandler(log_stream)
    memory_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    memory_handler.setFormatter(formatter)
    logger.addHandler(memory_handler)

    # Create and configure the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_log_output():
    return log_stream.getvalue()
