import argparse
import sys
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

from settings.cfg_client_log import logger
from settings.messages import action_auth, action_join, action_leave, action_msg, action_presence, action_quit
from settings.utils import get_message, log, send_message
from settings.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, INDENT, RESPONSE

NICKNAME, SOCK = "", ""


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", nargs="?", type=str, default=DEFAULT_IP_ADDRESS)
    parser.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT)
    return parser


def my_except_hook(exctype, value, traceback):
    """Выводим человекочитаемый 'Disconnect from the server!', при нажатии CTR + C"""

    if exctype == KeyboardInterrupt:
        print(f"{INDENT}\n  Disconnect from the server  \n{INDENT}")
    else:
        sys.__excepthook__(exctype, value, traceback)


def parsing_action(message):
    """Разбирает сообщения от клиентов"""
    try:
        global NICKNAME, SOCK
        if message["action"] == "probe":
            send_message(SOCK, action_presence(NICKNAME))
        else:
            print(message["message"])
    except:
        logger.critical("An error occurred!")
        SOCK.close()


def parsing_response(message):
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
        SOCK.close()


def receive():
    while True:
        try:
            global NICKNAME, SOCK
            message = get_message(SOCK)
            for key in message.keys():
                if key == "action":
                    parsing_action(message)
                elif key == "response":
                    parsing_response(message)
        except:
            logger.critical("An error occurred!")
            SOCK.close()
            break


def write():
    global NICKNAME
    while True:
        start = input("")
        if start == "h":
            command = input(
                f"Выберите действие: \n"
                f"s - отправить сообщение ПОЛЬЗОВАТЕЛЮ,\n"
                f"g - отправть сообщение ГРУППЕ,\n"
                f"wg - вступить в группу\n"
            )
            if command == "s":
                to_name = input(f"Введите ник, кому вы хотели бы отправить сообщение: \n").capitalize()
                msg = input(f"Введите сообщение пользователю {to_name}: ")
                send_message(SOCK, action_msg(NICKNAME, msg, to_name))
            elif command == "g":
                to_room = "#" + input("Введите название группы, кому вы хотели бы отправить сообщение: ").capitalize()
                msg = input(f"Введите сообщение группе {to_room}: ")
                send_message(SOCK, action_msg(NICKNAME, msg, to_room))
            elif command == "wg":
                join_room = "#" + input("К какой группе вы хотите присоединица?: \n").capitalize()
                send_message(SOCK, action_join(NICKNAME, join_room))
        else:
            print(f"Для вывода списка комманд, наберите - 'h'")


def main(address):
    """Основной скрипт работы клиента"""

    global NICKNAME, SOCK
    NICKNAME = input("Choose your nickname: ").capitalize()
    sys.excepthook = my_except_hook  # Обрабатываем Ctr+C
    try:
        if not 1024 <= address.port <= 65535:
            raise ValueError
        logger.info(f"Connected to remote host - {address.addr}:{address.port} ")
    except ValueError:
        logger.critical("The port must be in the range 1024-6535")
        sys.exit(1)
    else:
        SOCK = socket(AF_INET, SOCK_STREAM)
        try:
            SOCK.connect((address.addr, address.port))
        except:
            print(f"Unable to connect")
            logger.critical("Unable to connect")
            sys.exit()
        else:
            receive_thread = Thread(target=receive)
            receive_thread.start()
            write_thread = Thread(target=write)
            write_thread.start()


if __name__ == "__main__":
    parser = createParser()
    address = parser.parse_args()

    main(address)
