import pickle
import socket
import logging

from threading import Thread

cache = []


class ClientThread(Thread):
    def __init__(self, conn):
        Thread.__init__(self)
        self.conn = conn
        print("Thread created with IP: %s PORT: %s" % (self.conn.getsockname()[0], self.conn.getsockname()[1]))

    # Send command TCP socket of data
    # First packet contains length of data
    def send(self, msg):
        total = 0
        self.conn.send(len(msg))
        while total < len(msg):
            sent = self.conn.send(msg)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total += sent

    # Receive command for TCP socket of data
    # First packet contains length of data
    def receive(self):
        chunks = []
        total = pickle.loads(self.conn.recv(4096))
        print("Receiving data of size %s from client at %s" % (total, self.conn.getsockname()))
        while total > 0:
            chunk = self.conn.recv(4096)
            chunks.append(chunk)
            total -= len(chunk)
        return pickle.loads(''.join(chunks))

    def run(self):
        files = self.receive()
        if len(files) > 0:
            for file in files:
                cache.append(file)
        searchedFiles = []
        while True:
            data = self.receive().split()
            if data[0].upper() == "LIST":
                self.send(pickle.dumps(cache))
            elif data[0].upper() == "SEARCH":
                searchedFiles.clear()
                for file in cache:
                    search = file.split()
                    if search[0] == data[1]:
                        searchedFiles.append(file)
                if len(searchedFiles) > 0:
                    self.send(pickle.dumps(searchedFiles))
                else:
                    self.send(pickle.dumps("FILES NOT FOUND"))
            elif data[0].upper() == "RETRIEVE":
                for file in cache:
                    search = file.split()
                    if search[0] == data[1]:
                        self.send(pickle.dumps(file))
                    else:
                        self.send(pickle.dumps("FILE NOT FOUND"))
            elif data[0].upper() == "QUIT":
                self.conn.shutdown()
                self.conn.close()
                return


def server():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.bind(('127.0.0.1', 3000))
    serversock.listen(5)
    print(serversock.getsockname())
    while True:
        conn, address = serversock.accept()
        client = ClientThread(conn)
        client.start()


def main():
    server()


main()
