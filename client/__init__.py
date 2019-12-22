import socket
import threading

from client import function
from utils import make_msg, decode_msg


class Client():
    """ Contain all client commands """

    def __init__(self, server, port):
        print(server, port)
        self.server = server
        self.port = port
        self.user = None
        self.listen_thread = None
        self._conn = self.get_connection()
        if self._conn:
            self.run()

    def get_connection(self):
        """ Arg command: connect [ip server] port [port server] """
        try:
            client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connection.connect((self.server, self.port))
            print("Connect successful.")
            client_connection.sendall(bytes("I want to connect.", 'UTF-8'))
            return client_connection
        except Exception:
            print("Cannot connect to server.")
            return False

    def close_connection(self):
        """ Close connection """
        self._conn.send(bytes("bye", "UTF-8"))
        self._conn.close()

    def run(self):
        """ Running client commandline """
        new_thread = ListenThread(self._conn)
        new_thread.start()
        self.listen_thread = new_thread
        while True:
            try:
                command = input()
                if command.lower() == "close":
                    # Meet close command
                    break
                self.command_handle(command)
            except KeyboardInterrupt:
                self.close_connection()
        self.close_connection()

    def command_handle(self, command=""):
        """ Handling all input command """
        if command.startswith("login"):
            function.login(self._conn, command)

    def msg_handle(self, msg_recv):
        raw_data = decode_msg(msg_recv)
        msg_type = raw_data['type']
        msg_data = raw_data['data']
        print(msg_type, msg_data)


class ListenThread(threading.Thread):

    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        while True:
            msg_recv = self.connection.recv(8192)
            if msg_recv is not None:
                print(msg_recv)
