import logging
import os
from datetime import datetime

def setup_logger(log_dir: str = "logs"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"scanner_error_{timestamp}.log")

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File Handler (Errors and Warnings)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.WARNING) # Log warnings and errors to file
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console Handler (Info and up)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Avoid adding duplicates if setup called multiple times (though unlikely in this script structure)
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger, log_file
