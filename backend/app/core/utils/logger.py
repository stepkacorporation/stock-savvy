import logging
from logging.handlers import RotatingFileHandler

from django.conf import settings


def add_file_logger(logger: logging.RootLogger) -> logging.RootLogger:
    """
    Configures logging to a file for the logger.
    It takes values from the LOGGING file variable settings.py.

    Parameters:
        logger (logging.RootLogger): Root logger object to which the file handler will be added.

    Returns:
        logging.RootLogger: The logger object with the file handler configured.
    """

    handler_settings = settings.LOGGING.get('handlers').get('celery')
    formatter_settings = settings.LOGGING.get('formatters').get('verbose')
    logger_settings = settings.LOGGING.get('loggers').get('celery')

    file_handler = RotatingFileHandler(
        filename=handler_settings.get('filename'),
        maxBytes=handler_settings.get('maxBytes'),
        backupCount=handler_settings.get('backupCount'),
    )
    formatter = logging.Formatter(fmt=formatter_settings.get('format'), style=formatter_settings.get('style'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(logger_settings.get('level'))
    logger.propagate = logger_settings.get('propagate')

    return logger
