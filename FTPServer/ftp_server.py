from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

# creates FTP server using ThreadedFTPServer from pyftpdlib
def main():
    # Creates an authorizer for login verification
    authorizer = DummyAuthorizer()
    # Adds one set of login credentials to handle one user
    authorizer.add_user("user", "pass", ".", perm="elradfmwMT")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Connected"


    # Sets server to listen on address 127.0.0.1 while binding to port 3000
    address = ("127.0.0.1", 3000)
    server = ThreadedFTPServer(address, handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
