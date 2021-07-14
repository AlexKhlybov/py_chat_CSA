import re
import argparse
import logging
from time import sleep
from icecream import ic
from socket import *
from select import select
from threading import Thread
import logs.cfg_server_log as log_config
from common.decorators import try_except_wrapper
from common.descriptors import Port
from common.codes import *
from common.request_body import Msg, MsgRoom, Room
from common.utils import *
from common.metacls import ServerVerifier


class ServerThread(Thread):
    __slots__ = ('func', 'logger')

    def __init__(self, func, logger):
        super().__init__()
        self.func = func
        self.logger = logger
        self.daemon = True

    @try_except_wrapper
    def run(self):
        self.func()


# class Server(metaclass=ServerVerifier):
class Server():
    __slots__ = ('bind_addr', '_port', 'logger', 'socket', 'clients', 'users', 'rooms', 'commands', 'listener', 'subscribers')

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5
    port = Port('_port')

    def __init__(self, bind_addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.bind_addr = bind_addr
        self.port = port
        self.clients = []
        self.users = {}
        self.subscribers = {}
        self.rooms = {}

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.settimeout(0.5)
        self.socket.bind((self.bind_addr, self.port))
        self.logger.info(f'Config server port - {self.port}| Bind address - {self.bind_addr}')
        self.socket.listen(request_count)
        self.listener = ServerThread(self.__listen, self.logger)
        self.listener.start()
        self.__console()

    def __console(self):
        while True:
            msg = input('Enter command:\n')
            if msg.upper() == 'Q':
                break
            if msg[0] == '#':
                msg = msg[1:]

            command, *args = msg.split(' ')
            if command in self.commands:
                res = self.commands[command](*args)

    def __listen(self):
        self.logger.info('Start listen')
        while True:
            try:
                client, addr = self.socket.accept()
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)
            else:
                self.logger.info(f'Connection from {addr}')
                self.clients.append(client)

            i_clients, o_clients = [], []
            try:
                i_clients, o_clients, ex = select(self.clients, self.clients, [], self.TIMEOUT)
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)

            requests = self.__get_requests(i_clients)
            if requests:
                self.__send_responses(requests, o_clients)

    @try_except_wrapper
    def __get_requests(self, i_clients):
        requests = {}
        for client in i_clients:
            try:
                request = get_data(client)
                requests[client] = request

                if request.action == RequestAction.PRESENCE:
                    if request.body in self.users:
                        requests.pop(client)
                        send_data(client, Response(CONFLICT))
                        self.clients.remove(client)
                    else:
                        self.users[request.body] = client
                elif request.action == RequestAction.QUIT:
                    self.__client_disconnect(client)
            except (ConnectionError, ValueError):
                self.__client_disconnect(client)
            except Exception as e:
                raise e
        return requests

    @try_except_wrapper
    def __send_responses(self, requests, o_clients):

        for client, i_req in requests.items():
            other_clients = [c for c in o_clients if c != client]
            self.logger.info(client)
            self.logger.info(i_req)

            if i_req.action == RequestAction.PRESENCE:
                self.__send_to_client(client, Response(OK))
                self.__send_to_all(other_clients, Response(BASIC, f'{i_req.body} connected'))

            elif i_req.action == RequestAction.QUIT:
                self.__client_disconnect(client)

            elif i_req.action == RequestAction.MESSAGE:
                if not re.match(r'#', i_req.body['to']):
                    msg = Msg.from_dict(i_req.body)
                    if msg.to.upper() != 'ALL' and msg.to in self.users:
                        self.__send_to_client(self.users[msg.to], Response(BASIC, str(msg)))
                    else:
                        self.__send_to_all(other_clients, Response(BASIC, str(msg)))
                else:
                    msg = MsgRoom.from_dict(i_req.body)
                    if msg.to in self.rooms:
                        room = self.rooms[msg.to]
                        room_clients = [v for k, v in room.get_dict().items() if k != msg.sender]
                        if len(room_clients):
                            if msg.sender in room.get_dict():
                                self.__send_to_all(room_clients, Response(BASIC, str(msg)))
                            else:
                                self.__send_to_client(self.users[msg.sender], Response(ACCESS))
                    else:
                        self.__send_to_client(self.users[msg.sender], Response(NOT_FOUND))
                        subscribers = {}
                        subscribers[msg.sender] = self.users[msg.sender]
                        self.rooms[msg.to] = Room(msg.to, subscribers)
                        sleep(0.5)
                        self.__send_to_client(self.users[msg.sender], Response(BASIC, f'Chat {msg.to} created!'))
                        sleep(0.5)
                        self.__send_to_client(self.users[msg.sender], Response(BASIC, f'Now you can send a message to the chat {msg.to}'))
                
            elif i_req.action == RequestAction.JOIN:
                user = [k for k, v in self.users.items() if v == client]
                room = self.rooms[i_req.body]
                room.get_dict()[user[0]] = client
                room_clients = [v for k, v in room.get_dict().items() if k != user[0]]
                self.__send_to_all(room_clients, Response(BASIC, f'{user[0]} JOINED to chat - {i_req.body}!'))

            elif i_req.action == RequestAction.LEAVE:
                user = [k for k, v in self.users.items() if v == client]
                room = self.rooms[i_req.body]
                room.get_dict().pop(user[0])
                room_clients = room.get_dict().values()
                self.__send_to_all(room_clients, Response(BASIC, f'{user[0]} LEFT chat!'))

            elif i_req.action == RequestAction.COMMAND:
                command, *args = i_req.body.split()
                user = [u for u, c in self.users.items() if c == client].pop()
                args.insert(0, user)
                o_resp = self.__execute_command(command, *args)
                self.__send_to_client(client, o_resp)
            else:
                self.__send_to_client(client, Response(INCORRECT_REQUEST))
                self.logger.error(f'Incorrect request:\n {i_req}')

    @try_except_wrapper
    def __send_to_client(self, client, resp):
        try:
            send_data(client, resp)
        except ConnectionError:
            self.__client_disconnect(client)
        except Exception as e:
            raise e

    def __send_to_all(self, clients, resp):
        for cl in clients:
            self.__send_to_client(cl, resp)

    @try_except_wrapper
    def __client_disconnect(self, client):
        self.clients.remove(client)
        disconnected_user = [u for u, c in self.users.items() if c == client].pop()
        self.users.pop(disconnected_user)
        disconnection_response = Response(BASIC, f'{disconnected_user} disconnected')
        for cl in self.clients:
            send_data(cl, disconnection_response)

    def __execute_command(self, command, *args):
        if command in self.commands:
            answer = self.commands[command](*args)
            if answer is False:
                return Response(SERVER_ERROR, 'Command error')
            elif isinstance(answer, list):
                answer = [str(a) for a in answer]
                return Response(ANSWER, answer)
            elif answer is None:
                return Response(ANSWER, 'Done')
            return Response(ANSWER, answer)
        else:
            return Response(INCORRECT_REQUEST, 'Command not found')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, nargs='?', help='Port [default=7777]')
    parser.add_argument("-a", "--addr", type=str, default=DEFAULT_IP_ADDRESS, nargs='?', help='Bind address')
    return parser


def run():
    args = parse_args()
    server = Server(args.addr, args.port)
    server.start()


if __name__ == "__main__":
    run()