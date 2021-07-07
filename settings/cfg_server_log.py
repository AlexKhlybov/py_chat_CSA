import logging
from logging.handlers import TimedRotatingFileHandler

from settings.variables import ENCODING, LOG_FILENAME, LOGGER_NAME, WHEN_INTERVAL

FILE_LOG_LVL = logging.INFO

server_formatter = logging.Formatter(
    f"%(asctime)-5s - %(levelname)-5s | %(module)-5s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
)

logHandler = TimedRotatingFileHandler(LOG_FILENAME, when=WHEN_INTERVAL, interval=1, encoding=ENCODING)
logHandler.setFormatter(server_formatter)


logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logHandler)
logger.setLevel(FILE_LOG_LVL)
