import os
from types import ClassMethodDescriptorType

# Порт по умолчанию
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = "127.0.0.1"
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длина сообщений в байтах
BUFFER_SIZE = 2048
# Кодировка проекта
ENCODING = "utf-8"
# Тайм-аут
TIMEOUT = 0.2
WAIT = 10

DEFAULT_SERVER = "server"


# Красивости
INDENT = 30 * "-"


TYPE = 'type'
REQUEST = 'request'
RESPONSE = 'response'

ACTION = 'action'
TIME = 'time'
BODY = 'body'
CODE = 'code'
MESSAGE = 'message'
USERNAME = 'username'
ROOMNAME = 'roomname'
SUBSCRIBERS = 'subscribers'
SENDER = 'sender'
TO = 'to'
TEXT = 'text'


class RequestAction:
    PRESENCE = 'presence'
    MESSAGE = 'msg'
    QUIT = 'quit'
    JOIN = 'join'
    LEAVE = 'leave'
    COMMAND = 'command'

