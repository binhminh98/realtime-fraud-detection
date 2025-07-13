"""
Modules to add logging capabilities to the application.
"""

import logging
import os
from pathlib import Path


def get_logger(
    name: str,
    write_to_file: bool = False,
    log_filepath: str | Path | None = None,
) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger instance.
    """
    logger = logging.getLogger(name)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if write_to_file:
        if not log_filepath:
            log_filepath = Path(f"logs/{name}/{name}.log")
            log_filepath.parent.mkdir(parents=True, exist_ok=True)
        else:
            directory = os.path.dirname(log_filepath)
            if not os.path.exists(directory):
                if directory:
                    os.makedirs(directory, exist_ok=True)

        file_handler = logging.FileHandler(log_filepath)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.WARNING)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)

    return logger
