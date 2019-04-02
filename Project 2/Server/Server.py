import pickle
import socket
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
        message = pickle.dumps(msg)
        total = 0
        self.conn.send(pickle.dumps(len(message)))
        while total < len(message):
            sent = self.conn.send(message)
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
        data = []
        for item in chunks:
            data.append(pickle.loads(item))
        return b''.join(data)

    def run(self):
        files = self.receive()
        print("Cache updated with data %s " % files)
        if len(files) > 0:
            for file in files:
                cache.append(file)
        print("Cache updated with data %s " % files)
        searched_files = []
        while True:
            data = self.receive().split()
            if data[0].upper() == "LIST":
                self.send(pickle.dumps(cache))
            elif data[0].upper() == "SEARCH":
                searched_files.clear()
                for file in cache:
                    search = file.split()
                    if search[0] == data[1]:
                        searched_files.append(file)
                if len(searched_files) > 0:
                    self.send(pickle.dumps(searched_files))
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
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('127.0.0.1', 3000))
    server_sock.listen(5)
    print(server_sock.getsockname())
    while True:
        conn, address = server_sock.accept()
        client = ClientThread(conn)
        client.start()


def main():
    server()


main()
