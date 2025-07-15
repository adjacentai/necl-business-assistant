import logging
import os
from src.config import LOGS_DIR

# Ensure the logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

def get_user_logger(user_id: int):
    """
    Creates and configures a logger for a specific user.
    Each user will have their own log file.
    """
    log_file_path = os.path.join(LOGS_DIR, f'user_{user_id}.txt')
    logger_name = f'user_{user_id}'
    
    logger = logging.getLogger(logger_name)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Use a file handler to write logs to a user-specific file
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    
    # Simple formatter with just the timestamp and message
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to the logger
    logger.addHandler(file_handler)
    
    # Prevent logs from propagating to the root logger, which might print to console
    logger.propagate = False

    return logger

def log_user_message(user_id: int, text: str):
    """Logs a message from the user."""
    logger = get_user_logger(user_id)
    logger.info(f"User: {text}")

def log_assistant_response(user_id: int, text: str):
    """Logs a response from the assistant."""
    logger = get_user_logger(user_id)
    logger.info(f"Assistant: {text}") 