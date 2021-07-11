import argparse
import sys
from time import sleep
from socket import AF_INET, AddressFamily, SOCK_STREAM, socket
from threading import Thread

from settings.cfg_client_log import logger
from settings.messages import action_auth, action_join, action_leave, action_msg, action_presence, action_quit
from settings.utils import get_message, log, send_message
from settings.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, INDENT, RESPONSE


class Client:
    def __init__(self, addr, port, name):
        self.addr = addr
        self.port = port 
        self.nickname = name.capitalize() if name else name
        self.sock = ""
        self.actions = {
            "q": "Выход",
            "s": "Отправить сообщение ПОЛЬЗОВАТЕЛЮ",
            "g": "Отправить сообщение ГРУППЕ",
            "wg": "Вступить в ГРУППУ"
        }

    @property
    def help_info(self):
        print(INDENT)
        return '\n'.join(
            [f'{key} - {action}' for key, action in self.actions.items()])

    def parsing_action(self, message):
        """Разбирает сообщения от клиентов"""
        try:
            if message["action"] == "probe":
                send_message(self.sock, action_presence(self.nickname))
            else:
                print(message["message"])
        except:
            logger.critical("An error occurred!")
            self.sock.close()

    def parsing_response(self, message):
        """Разбирает ответы от сервера"""
        code = message["response"]
        alert = message["alert"]
        try:
            print(f"{message['alert']}")
            if code == 101 or code == 102 or code == 200 or code == 202:
                logger.info((f"{code} - {alert}"))
            elif code == 400 or code == 401 or code == 402 or code == 404 or code == 409:
                logger.error((f"{code} - {alert}"))
            else:
                logger.critical((f"{code} - {alert}"))
        except:
            logger.critical("An error occurred!")
            self.sock.close()

    def receive(self):
        while True:
            try:
                message = get_message(self.sock)
                for key in message.keys():
                    if key == "action":
                        self.parsing_action(message)
                    elif key == "response":
                        self.parsing_response(message)
            except:
                logger.critical("An error occurred!")
                self.sock.close()
                break

    def write(self):
        print(self.help_info)
        while True:
            command = input(f"Выберите действие (для справки введите - h): \n")
            if command == "h":
                print(self.help_info)
            if command == "s":
                to_name = input(f"Введите ник, кому вы хотели бы отправить сообщение: \n").capitalize()
                msg = input(f"Введите сообщение пользователю {to_name}: ")
                send_message(self.sock, action_msg(self.nickname, msg, to_name))
            elif command == "g":
                to_room = "#" + input("Введите название группы, кому вы хотели бы отправить сообщение: ").capitalize()
                msg = input(f"Введите сообщение группе {to_room}: ")
                send_message(self.sock, action_msg(self.nickname, msg, to_room))
            elif command == "wg":
                join_room = "#" + input("К какой группе вы хотите присоединица?: \n").capitalize()
                send_message(self.sock, action_join(self.nickname, join_room))
            elif command == "q":
                self.sock.close()
                break
            else:
                print(f"Для вывода списка комманд, наберите - 'h'")

    def main(self):
        """Основной скрипт работы клиента"""
        if not self.nickname:
            print(self.nickname)
            self.nickname = input("Choose your nickname: ").capitalize()
        try:
            if not 1024 <= self.port <= 65535:
                raise ValueError
            logger.info(f"Connected to remote host - {self.addr}:{self.port} ")
        except ValueError:
            logger.critical("The port must be in the range 1024-6535")
            sys.exit(1)
        else:
            self.sock = socket(AF_INET, SOCK_STREAM)
            try:
                self.sock.connect((self.addr, self.port))
            except:
                print(f"Unable to connect")
                logger.critical("Unable to connect")
                sys.exit()
            else:
                receive_thread = Thread(target=self.receive)
                receive_thread.start()
                sleep(5)
                write_thread = Thread(target=self.write)
                write_thread.start()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", nargs="?", type=str, default=DEFAULT_IP_ADDRESS)
    parser.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT)
    parser.add_argument("name", nargs="?", type=int, default=None)
    return parser

def run():
    args = parse_args()
    client = Client(args.addr, args.port, args.name)
    client.main()


if __name__ == "__main__":
    run()
