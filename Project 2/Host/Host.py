import os
import pickle
import socket

from threading import Thread
from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

username = ''
prompt = "-"*10 + "\nLIST - List all available files\nSEARCH [KEYWORD] - List all files with keyword" \
    "\nRETRIEVE [FILENAME] - Retrieve requested file from host\nQUIT - Disconnect from server\n" + "-"*10 + "\n"


class Server(Thread):
    def __init__(self, hostname, port):
        Thread.__init__(self)
        self.hostname = hostname
        self.port = port

    def server_init(self):
        authorizer = DummyAuthorizer()
        authorizer.add_anonymous(os.getcwd(), perm="elradfmwMT")
        handler = FTPHandler
        handler.authorizer = authorizer
        server = ThreadedFTPServer((self.hostname, self.port), handler)
        server.serve_forever()

    def run(self):
        self.server_init()


def clients():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 3000))
    files = os.listdir(os.getcwd())
    message = pickle.dumps(files)
    client_sock.send(pickle.dumps(len(message)))
    total = 0
    while total < len(message):
        sent = client_sock.send(message)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total += sent
    while True:
        client_input = input(prompt)
        msg = pickle.dumps(client_input)
        client_sock.send(pickle.dumps(len(msg)))
        client_sock.send(msg)
        data = client_receive(client_sock)
        if (data.split())[0] == (client_input.split())[1]:
            client = FTP()
            client.connect((data.split())[1], 3000)
            file = open((client_input.split())[1], "wb")
            client.retrbinary((client_input.split())[1], file.write)
            file.close()
            client.close()
        print(data)


def client_receive(cs):
    chunks = []
    total = pickle.loads(cs.recv(4096))
    while total > 0:
        chunk = cs.recv(4096)
        chunks.append(chunk)
        total -= len(chunk)
    data = []
    for item in chunks:
        data.append(pickle.loads(item))
    return b''.join(data)


def main():
    server_setup = input("Enter username, hostname, and port - [USERNAME] [HOSTNAME] [PORT]\n").split()
    username = server_setup[0]
    server = Server(server_setup[1], server_setup[2])
    server.start()
    clients()


main()
