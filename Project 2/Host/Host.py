import os
import pickle
import socket

from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

username = ''
client = FTP()
prompt = "-"*10 + "\nLIST - List all available files\nSEARCH [KEYWORD] - List all files with keyword" \
    "\nRETRIEVE [FILENAME] - Retrieve requested file from host\nQUIT - Disconnect from server\n" + "-"*10 + "\n"


def serverInit(user, hostname, port):
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(os.getcwd(), perm="elradfmwMT")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = ThreadedFTPServer(hostname, port, handler)
    server.serve_forever()
    return user


def retrieve(hostname, port, filename):
    client.connect(hostname, port)
    file = open(filename, 'wb')
    client.retrbinary("RETR " + filename, file.write)
    file.close()


def connect(hostname, port):
    client.connect(hostname, port)


def main():
    serverSetup = input("Enter username, hostname, and port - [USERNAME] [HOSTNAME] [PORT]").split()
    serverInit(serverSetup[0], serverSetup[1], serverSetup[2])
