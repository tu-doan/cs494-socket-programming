""" This is serverside source code """
import socket
from .database import test

LOCALHOST = "127.0.0.1"
PORT = 8080
LIST_CLIENTS = []


def run():
    """ Starting server """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    test()
    print("Server started")
    print("Waiting for client request..")
    from . import client_thread
    while True:
        try:
            server.listen(1)
            clientsock, client_address = server.accept()
            LIST_CLIENTS.append({'sock': clientsock, 'uid': 0})
            newthread = client_thread.ClientThread(client_address, clientsock)
            newthread.start()
            print("Now we have %s client(s) connected: " % len(LIST_CLIENTS))
        except KeyboardInterrupt:
            break
