import logging
import os
import sys

# This function will be set as the global exception hook
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    A custom exception handler that logs any unhandled exceptions before exiting.
    """
    # Check if a logger has been configured
    logger = logging.getLogger("hizawye_logger")
    if not logger.hasHandlers():
        # If no logger is set up, just print the exception to the console
        # This prevents errors if an exception occurs before logging is configured
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("--- UNHANDLED EXCEPTION ---", exc_info=(exc_type, exc_value, exc_traceback))
    logger.critical("--- HIZAWYE AI IS CRASHING ---")

def setup_logger():
    """Sets up a structured file logger and exception handler for the project."""
    
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger = logging.getLogger("hizawye_logger")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    log_path = os.path.join(logs_dir, "hizawye_runtime.log")
    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    
    # Set the custom exception handler
    sys.excepthook = handle_exception

    return logger

