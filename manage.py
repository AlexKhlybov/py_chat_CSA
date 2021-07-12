import argparse

from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, DEFAULT_SERVER
from src.client import Client
from src.server import Server


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default=DEFAULT_SERVER)
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("-a", "--addr", type=str, default=DEFAULT_IP_ADDRESS)
    return parser


def start():
    parser = parse_args()
    namespace = parser.parse_args()
    return namespace


if __name__ == "__main__":
    ns = start()
    if ns.type == "server":
        server = Server(ns.addr, ns.port)
        server.start()
    elif ns.type == "client":
        client = Client(ns.addr, ns.port)
        client.start()
