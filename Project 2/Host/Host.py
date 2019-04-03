import os
import socket
import pickle
import time

from threading import Thread

prompt = "-"*10 + "\nLIST - List all available files\nSEARCH [KEYWORD] - List al files with keyword" \
    "\nRETRIEVE [FILENAME] - Retrieve requested file from host\nQUIT - Disconnect from server\n" + "-"*10 + "\n"


class Server(Thread):
    def __init__(self, hostname, port):
        Thread.__init__(self)
        self.hostname = hostname
        self.port = port

    def server_init(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.hostname, int(self.port)))
        server_sock.listen(5)
        while True:
            conn, address = server_sock.accept()
            print("Connecting with %s" % conn)
            client = Client(conn)
            client.start()

    def run(self):
        print("Starting server at IP: %s PORT: %s" % (self.hostname, self.port))
        self.server_init()


class Client(Thread):
    def __init__(self, conn):
        Thread.__init__(self)
        self.connection = conn
        self.cache = []

    def send(self, msg):
        message = pickle.dumps(msg)
        length = pickle.dumps(len(message))
        total = 0
        self.connection.send(length)
        while total < len(message):
            sent = self.connection.send(message[total:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total += sent

    def receive(self):
        chunks = []
        total = pickle.loads(self.connection.recv(4096))
        while total > 0:
            data = self.connection.recv(4096)
            chunk = pickle.loads(data)
            chunks.append(chunk)
            total -= len(data)
        return ''.join(chunks)

    def run(self):
        self.cache = os.listdir(os.getcwd())
        while True:
            data = self.receive()
            if (data.split())[0] == "RETR":
                for item in self.cache:
                    if (data.split())[1] == item:
                        message = b''
                        file = open(item, "rb")
                        for line in file:
                            message += line
                        file.close()
                        self.send(message)
                        return


def send(sock, msg):
    message = pickle.dumps(msg)
    length = pickle.dumps(len(message))
    total = 0
    sock.send(length)
    time.sleep(1)
    while total < len(message):
        sent = sock.send(message[total:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total += sent


def receive(connection):
    chunks = []
    total = pickle.loads(connection.recv(4096))
    while total > 0:
        data = connection.recv(4096)
        # chunk = pickle.loads(data)
        chunks.append(data)
        total -= len(data)
    data_array = b''.join(chunks)
    return pickle.loads(data_array)


def download(file, hostname, port):
    sock = socket.socket()
    sock.connect((hostname, int(port)))
    message = pickle.dumps("RETR " + file)
    length = len(message)
    sock.send(pickle.dumps(length))
    time.sleep(1)
    sock.send(message)
    total = pickle.loads(sock.recv(4096))
    chunks = []
    while total > 0:
        chunk = sock.recv(4096)
        chunks.append(pickle.loads(chunk))
        total -= len(chunk)
    data = b''.join(chunks)
    file_output = open(file.split()[0], "wb")
    file_output.write(data)
    file_output.close()


def main():
    cache = []
    files = os.listdir(os.getcwd())
    for file in files:
        cache.append(file)
    connection = socket.socket()
    connection.connect(('127.0.0.1', 3000))
    server_settings = connection.getsockname()
    server = Server(server_settings[0], server_settings[1])
    server.start()
    send(connection, cache)
    while True:
        command = input(prompt)
        if command.split()[0].upper() == "RETRIEVE":
            send(connection, command)
            response = receive(connection).split()
            download(response[0], response[1], response[2])
        elif command.split()[0].upper() == "QUIT":
            send(connection, "QUIT")
            connection.close()
        else:
            send(connection, command)
            response = receive(connection)
            for item in response:
                print(item + "\n")


main()
