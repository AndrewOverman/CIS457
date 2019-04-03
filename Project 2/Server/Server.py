import socket
import pickle
import time

from threading import Thread

cache = []


class ClientThread(Thread):
    global cache

    def __init__(self, conn):
        Thread.__init__(self)
        self.connection = conn
        print("Thread created with IP: %s PORT: %s" %
              (self.connection.getpeername()[0], self.connection.getpeername()[1]))

    def send(self, msg):
        message = pickle.dumps(msg)
        length = pickle.dumps(len(message))
        print("Sending data of size %s to client at %s" % (len(message), self.connection.getpeername()))
        total = 0
        self.connection.send(length)
        time.sleep(1)
        while total < len(message):
            sent = self.connection.send(message[total:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total += sent

    def receive(self):
        chunks = []
        total = pickle.loads(self.connection.recv(4096))
        print("Receiving data of size %s from client at %s" % (total, self.connection.getpeername()))
        while total > 0:
            data = self.connection.recv(4096)
            chunk = pickle.loads(data)
            chunks.append(chunk)
            total -= len(data)
        return ''.join(chunks)

    def update_cache(self):
        total = pickle.loads(self.connection.recv(4096))
        print("Receiving host contents of size %s from client at %s" % (total, self.connection.getpeername()))
        data = self.connection.recv(4096)
        host_cache = pickle.loads(data)
        for item in host_cache:
            cache.append(item + " " + self.connection.getpeername()[0] + " " + str(self.connection.getpeername()[1]))
        print("Updated cache with %s" % host_cache)
        print("Current cache %s" % cache)

    def search(self, keyword):
        searched = []
        for file in cache:
            if (file.split())[0] == keyword:
                searched.append(file)
        if len(searched) == 0:
            return "NO_FILES_FOUND"
        return searched

    def retrieve(self, keyword):
        for file in cache:
            if (file.split())[0] == keyword:
                return file
        return "FILE_NOT_FOUND"

    def run(self):
        self.update_cache()
        while True:
            data = self.receive().split()
            if data[0].upper() == "LIST":
                print("Sending cache to %s " % self.connection.getpeername()[0])
                self.send(cache)
            elif data[0].upper() == "SEARCH":
                print("Sending filtered cache to %s " % self.connection.getpeername()[0])
                searched_files = self.search(data[1])
                self.send(searched_files)
            elif data[0].upper() == "RETRIEVE":
                self.send(self.retrieve(data[1]))
            elif data[0].upper() == "QUIT":
                print("Closing connection with %s " % self.connection.getpeername()[0])
                temp_cache = []
                for item in cache:
                    if int(item.split()[2]) == int(self.connection.getpeername()[1]):
                        temp_cache.append(item)
                self.connection.close()
                for item in temp_cache:
                    cache.remove(item)
                break


def server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('127.0.0.1', 3000))
    server_sock.listen(5)
    print("Cache server running on IP: %s PORT: %s" % server_sock.getsockname())
    while True:
        conn, address = server_sock.accept()
        client = ClientThread(conn)
        client.start()


server()
