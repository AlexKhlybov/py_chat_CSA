import inspect
import logging
from pickle import dumps, loads

from settings.variables import BUFFER_SIZE, ENCODING, LOG_FILENAME


def get_message(sock):
    """
    Утилита приема и декодирования сообщения.
    Принимает байты и выдает словарь, если принято что - то другое отдает ошибку значения

    """
    encoded_response = sock.recv(BUFFER_SIZE)
    if isinstance(encoded_response, bytes):
        response = loads(encoded_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, msg):
    """
    Утилита кодирования и отправки сообщения.
    Принимает словарь и отправляет его.

    """
    encoded_message = dumps(msg)
    sock.send(encoded_message)


logFormatter = logging.Formatter(f"%(asctime)-5s - %(levelname)-5s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

logHandler = logging.FileHandler(LOG_FILENAME, encoding=ENCODING)
logHandler.setFormatter(logFormatter)

logger = logging.getLogger("app." + __name__)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


def log(func):
    def wrapper(*args, **kwargs):
        logger.info(f'function name: "{func.__name__}", arguments: {args}, {kwargs}')
        r = func(*args, **kwargs)
        logger.info(f'Function "{func.__name__}" called from a function "{inspect.stack()[1][3]}"')
        return r

    return wrapper
