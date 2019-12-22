""" This is serverside source code """
import socket
from . import client_thread
LOCALHOST = "127.0.0.1"
PORT = 8080


def run():
    """ Starting server """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = client_thread.ClientThread(clientAddress, clientsock)
        newthread.start()
