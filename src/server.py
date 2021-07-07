import argparse
import select
import sys
from re import match
from socket import AF_INET, SOCK_STREAM, socket
from time import sleep

from settings.cfg_server_log import logger
from settings.response import action_msg, action_probe, get_101, get_102, get_201, get_401, get_404
from settings.utils import get_message, log, send_message
from settings.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, INDENT, MAX_CONNECTIONS, TIMEOUT, WAIT

CLIENTS = []
NICKNAMES = []
ROOMS = [{"room_name": "#all", "clients": CLIENTS, "nicknames": NICKNAMES}]


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("-a", "--addr", type=str, default=DEFAULT_IP_ADDRESS)
    return parser


def my_except_hook(exctype, value, traceback):
    """Выводим человекочитаемый 'Server STOP', при нажатии CTR + C"""

    if exctype == KeyboardInterrupt:
        print(f"{INDENT}\n\tServer STOP!\n{INDENT}")
    else:
        sys.__excepthook__(exctype, value, traceback)


def read_requests(r_clients, all_clients):
    """Чтение запросов из списка клиентов"""

    responses = {}  # Словарь ответов сервера вида {сокет: запрос}
    for sock in r_clients:
        try:
            data = get_message(sock)
            responses[sock] = data
        except:
            print(f"Client {sock.fileno()} {sock.getpeername()} DISCONNECTED")
            logger.info(f"Client {sock.fileno()} {sock.getpeername()} DISCONNECTED")
            all_clients.remove(sock)
    return responses


def parsing_requests(requests):
    """Разбираем клиентское сообщение"""

    for request in requests.values():
        if request["action"] == "msg":
            if match(r"#", request["to"]):
                room_msg(request)
            else:
                private_msg(request)
        elif request["action"] == "join":
            room = get_room(request["room"])
            client = CLIENTS[NICKNAMES.index(request["from"])]
            if room == False:
                room = get_new_room(request["room"])
                room["clients"].append(client)
                room["nicknames"].append(request["from"])
                send_message(client, get_404())
                sleep(0.5)
                send_message(client, get_201(request["room"]))
                sleep(0.5)
                send_message(client, get_102(f"Вы подключились к чату {request['room']}"))
            else:
                room["clients"].append(client)
                room["nicknames"].append(request["from"])
                room_msg(request)


def private_msg(msg):
    """Отправляем личное сообщение"""

    global NICKNAMES, CLIENTS
    if not NICKNAMES.count(msg["to"]) == 0:
        for nick in NICKNAMES:
            if nick == msg["to"]:
                client = CLIENTS[NICKNAMES.index(nick)]
                send_message(client, msg)
    else:
        client = CLIENTS[NICKNAMES.index(msg["from"])]
        send_message(client, get_404())


def room_msg(msg):
    """Отправляем сообщение в конкретный чат"""

    try:
        to_name = msg["to"]
    except:
        to_name = msg["room"]
        msg["message"] = f"{to_name} подключился к чату!"
    finally:
        if to_name == "#all":
            broadband(msg)
        else:
            room = get_room(to_name)
            client = CLIENTS[NICKNAMES.index(msg["from"])]
            if not room:
                room = get_new_room(to_name)
                room["clients"].append(client)
                room["nicknames"].append(msg["from"])
                send_message(client, get_404())
                sleep(0.5)
                send_message(client, get_201(to_name))
                sleep(0.5)
                send_message(client, get_102(f"Вы подключились к чату {to_name}"))
            else:
                if not room["nicknames"].count(msg["from"]) == 0:
                    for client in room["clients"]:
                        # send_message(client, get_101(NICKNAMES[CLIENTS.index(client)]))
                        send_message(
                            client, action_msg(f"<{msg['from']}>: {msg['message']}", NICKNAMES[CLIENTS.index(client)])
                        )
                else:
                    send_message(
                        client,
                        get_102(
                            f"Вы не можете отправить сообщение в чат {msg['to']}\n"
                            f"Сначала подключитесь к чату, потом сможете отправлять сообщение!"
                        ),
                    )


def broadband(msg):
    """Флудилка, сообщения всем клиентам"""

    global CLIENTS
    for client in CLIENTS:
        try:
            send_message(client, action_msg(msg["message"], msg["to"]))
        except:  # Сокет недоступен, клиент отключился
            print(f"Client {client.fileno()} {client.getpeername()} DISCONNECTED")
            client.close()
            CLIENTS.remove(client)


def get_room(room_name):
    """Возвращает требуемый чат или False"""

    global ROOMS
    for room in ROOMS:
        if room["room_name"] == room_name:
            return room
        else:
            continue
    return False


def get_new_room(room_name):
    """Создает и возвращает новый чат"""

    global ROOMS
    room_new = {"room_name": room_name, "clients": [], "nicknames": []}
    ROOMS.append(room_new)
    return room_new


def main(address):
    """Основной скрипт работы сервера"""

    sys.excepthook = my_except_hook  # Обрабатываем Ctr+C
    sock = socket(AF_INET, SOCK_STREAM)

    try:
        if not 1024 <= address.port <= 65535:
            raise ValueError
    except ValueError:
        logger.critical("The port must be in the range 1024-6535")
        sys.exit(1)
    else:
        sock.bind((address.addr, address.port))
        sock.listen(MAX_CONNECTIONS)
        sock.settimeout(TIMEOUT)
        logger.info(f"The server is RUNNING on the port: {address.port}")
        print(f"The server is RUNNING on the port: {address.port}")
    finally:
        global ROOMS, NICKNAMES, CLIENTS
        while True:
            try:
                conn, addr = sock.accept()
            except OSError as e:
                pass  # timeout вышел
            else:
                logger.info(f"Connected with {str(addr)}")
                send_message(conn, action_probe())
                cli_probe = get_message(conn)
                # TODO сделать проверку на сшществование такого ника
                nickname = cli_probe["user"]["account_name"]
                for room in ROOMS:
                    # TODO проверить try-except если не будет room_name
                    if not room["room_name"] == "#all":
                        continue
                    else:
                        NICKNAMES.append(nickname)
                        CLIENTS.append(conn)
                        logger.info(f"{nickname} joined!")
                        send_message(conn, get_101("Connected server!"))
                        break
            finally:
                r = []
                w = []
                try:
                    r, w, e = select.select(CLIENTS, CLIENTS, [], WAIT)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                requests = read_requests(r, CLIENTS)  # Сохраним запросы клиентов
                if requests:
                    parsing_requests(requests)


if __name__ == "__main__":
    parser = createParser()
    address = parser.parse_args()

    main(address)
