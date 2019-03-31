import pickle
import socket

from threading import Thread

cache = []


class ClientThread(Thread):
    def __init__(self, conn):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = conn

    def send(self, msg):
        total = 0
        while total < msglen:

    def receive(self):
        chunks = []
        total = 0



def server():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.bind(('127.0.0.1', 3000))
    serversock.listen(5)
    while True:
        conn, address = serversock.accept()
        client = ClientThread(conn)
        client.run()


def main():
    server()
