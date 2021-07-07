import argparse

from settings.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, DEFAULT_SERVER
from src import client, server


def mainParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default=DEFAULT_SERVER)
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("-a", "--addr", type=str, default=DEFAULT_IP_ADDRESS)
    return parser


def start():
    parser = mainParser()
    namespace = parser.parse_args()
    return namespace


if __name__ == "__main__":

    what_run = start()
    if what_run.type == "server":
        server.main(what_run)
    elif what_run.type == "client":
        client.main(what_run)
