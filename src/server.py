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


class Server:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = port
        self.clients = []
        self.nicknames = []
        self.rooms = [
            {
                "room_name": "#all",
                "clients": self.clients,
                "nicknames": self.nicknames
            }
        ]
    
    def read_requests(self, r_clients):
        """Чтение запросов из списка клиентов"""
        responses = {}  # Словарь ответов сервера вида {сокет: запрос}
        for sock in r_clients:
            try:
                data = get_message(sock)
                responses[sock] = data
            except:
                print(f"Client {sock.fileno()} {sock.getpeername()} DISCONNECTED")
                logger.info(f"Client {sock.fileno()} {sock.getpeername()} DISCONNECTED")
                self.clients.remove(sock)
        return responses

    def parsing_requests(self, requests):
        """Разбираем клиентское сообщение"""
        for request in requests.values():
            if request["action"] == "msg":
                if match(r"#", request["to"]):
                    self.room_msg(request)
                else:
                    self.private_msg(request)
            elif request["action"] == "join":
                room = self.get_room(request["room"])
                client = self.clients[self.nicknames.index(request["from"])]
                if room == False:
                    room = self.get_new_room(request["room"])
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
                    self.room_msg(request)

    def private_msg(self, msg):
        """Отправляем личное сообщение"""
        if not self.nicknames.count(msg["to"]) == 0:
            print(self.nicknames)
            print(self.clients)
            for nick in self.nicknames:
                if nick == msg["to"]:
                    client = self.clients[self.nicknames.index(nick)]
                    send_message(client, msg)
        else:
            client = self.clients[self.nicknames.index(msg["from"])]
            send_message(client, get_404())

    def room_msg(self, msg):
        """Отправляем сообщение в конкретный чат"""
        try:
            to_name = msg["to"]
        except:
            to_name = msg["room"]
            msg["message"] = f"{to_name} подключился к чату!"
        finally:
            if to_name == "#all":
                self.broadband(msg)
            else:
                room = self.get_room(to_name)
                client = self.clients[self.nicknames.index(msg["from"])]
                if not room:
                    room = self.get_new_room(to_name)
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
                                client, action_msg(f"<{msg['from']}>: {msg['message']}", self.nicknames[self.clients.index(client)])
                            )
                    else:
                        send_message(
                            client,
                            get_102(
                                f"Вы не можете отправить сообщение в чат {msg['to']}\n"
                                f"Сначала подключитесь к чату, потом сможете отправлять сообщение!"
                            ),
                        )

    def broadband(self, msg):
        """Флудилка, сообщения всем клиентам"""
        for client in self.clients:
            try:
                send_message(client, action_msg(msg["message"], msg["to"]))
            except:  # Сокет недоступен, клиент отключился
                print(f"Client {client.fileno()} {client.getpeername()} DISCONNECTED")
                client.close()
                self.clients.remove(client)

    def get_room(self, room_name):
        """Возвращает требуемый чат или False"""
        for room in self.rooms:
            if room["room_name"] == room_name:
                return room
            else:
                continue
        return False

    def get_new_room(self, room_name):
        """Создает и возвращает новый чат"""
        room_new = {"room_name": room_name, "clients": [], "nicknames": []}
        self.rooms.append(room_new)
        return room_new

    def main(self):
        """Основной скрипт работы сервера"""
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            if not 1024 <= self.port <= 65535:
                raise ValueError
        except ValueError:
            logger.critical("The port must be in the range 1024-6535")
            sys.exit(1)
        else:
            sock.bind((self.addr, self.port))
            sock.listen(MAX_CONNECTIONS)
            sock.settimeout(TIMEOUT)
            logger.info(f"The server is RUNNING on the port: {self.port}")
            print(f"The server is RUNNING on the port: {self.port}")
        finally:
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
                    for room in self.rooms:
                        # TODO проверить try-except если не будет room_name
                        if not room["room_name"] == "#all":
                            continue
                        else:
                            self.nicknames.append(nickname)
                            self.clients.append(conn)
                            logger.info(f"{nickname} joined!")
                            print(f"{nickname} joined!")
                            send_message(conn, get_101("Connected server!"))
                            break
                finally:
                    r = []
                    w = []
                    try:
                        r, w, e = select.select(self.clients, self.clients, [], WAIT)
                    except:
                        pass  # Ничего не делать, если какой-то клиент отключился
                    requests = self.read_requests(r_clients=r)  # Сохраним запросы клиентов
                    if requests:
                        self.parsing_requests(requests)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("-a", "--addr", type=str, default=DEFAULT_IP_ADDRESS)
    return parser

def run():
    args = parse_args()
    server = Server(args.addr, args.port)
    server.main()

if __name__ == "__main__":
    run()