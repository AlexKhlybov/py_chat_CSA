import os

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


# Протокол JIM основные ключи
ACTION = "message"
TIME = "time"
USER = "Dave"


# Прочие ключи используемые в протоколе
PRESENCE = "presence"
RESPONSE = "response"
ERROR = "error"
RESPONSE_DEFAULT_IP_ADDRESS = "response_default_ip_address"


# Ключи используемые в протоколе логирования
ROOT = os.getcwd()
DIR_LOG = "logs"

LOG_DIRECTORY = os.path.join(ROOT, DIR_LOG)
LOG_FILENAME = os.path.join(LOG_DIRECTORY, "app.log")

LOGGER_NAME = "app." + __name__

BACKUP_COUNT = 5
WHEN_INTERVAL = "D"


# Красивости
INDENT = 30 * "-"
