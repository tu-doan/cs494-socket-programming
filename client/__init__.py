import socket
import threading

from constant import *
from utils import make_msg, make_msg_encrypt


def run():
    """ Running client commandline """
    print(">>>Connect to server by typing: connect [server] port [port]")
    print(">>>Disconnect by typing: close")

    command = input("$ ")
    args = command.split(" ")

    if args[0].lower() != "connect":
        print("_ERROR_ Please connect first")
        return

    try:
        server = args[1] if len(args) > 1 else "127.0.0.1"
        port = int(args[3] if len(args) > 3 else "8080")
        client = Client(server, port)
    except Exception:
        print("[ERROR] Cannot connect. Please try later!")
        return

    listen_thread = ListenThread(client)
    listen_thread.start()
    while True:
        try:
            command = input()
            if command.lower() == "close":
                # Meet close command
                break
            client.command_handle(command)
        except KeyboardInterrupt:
            break
    client.close_connection()   # Close the connection
    exit(0)


class Client():
    """ Contain all client commands """

    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.user = None
        self.pkey = None
        self.listen_thread = None
        self._stop = False
        self._conn = self.get_connection()

    def get_connection(self):
        """ Arg command: connect [ip server] port [port server] """
        try:
            client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connection.connect((self.server, self.port))
            client_connection.sendall(bytes("I want to connect.", 'UTF-8'))

            # first receive message is private key
            msg_recv = client_connection.recv(8192)
            self.pkey = msg_recv
            print("Connect successful to %s:%s" % (self.server, self.port))
            return client_connection
        except Exception:
            raise Exception("Cannot connect to server.")

    def close_connection(self):
        """ Close connection """
        if not self._stop:
            self._stop = True
            self._conn.send(bytes("bye", "UTF-8"))
            self._conn.close()

    def listen(self):
        """ Receive message """
        if self._stop:
            return False

        msg_recv = self._conn.recv(8192)
        if msg_recv == b'':
            print("Connection to server broke.")
            self.close_connection()
            return False
        if msg_recv is not None:
            print(msg_recv)
            self.msg_handle(msg_recv)
        return True

    def command_handle(self, command=""):
        """ Handling all input commands """
        if command.startswith(CMD_LOGIN):
            self.login(command)
            return
        if command.startswith(CMD_REGISTER):
            self.register(command)
            return

    def msg_handle(self, msg_recv):
        """ Handling received messages """
        from utils import decode_msg
        raw_data = decode_msg(msg_recv)
        msg_type = raw_data['type']
        msg_data = raw_data['data']
        print(msg_type, msg_data)

    def login(self, command):
        """ Login user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for login")
            return

        password = getpass(">> Password: ")

        if command.startswith(CMD_LOGIN_ENCRYPT):
            username = args[2]
            data = {'username': username, 'password': password}
            msg = make_msg_encrypt(CMD_LOGIN_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {'username': username, 'password': password}
            msg = make_msg(CMD_LOGIN, data)
        self._conn.sendall(msg)

    def register(self, command):
        """ Register user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for register")
            return

        password = getpass(">> Password: ")

        if command.startswith(CMD_REGISTER_ENCRYPT):
            username = args[2]
            data = {'username': username, 'password': password}
            msg = make_msg_encrypt(CMD_REGISTER_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {'username': username, 'password': password}
            msg = make_msg(CMD_REGISTER, data)
        self._conn.sendall(msg)

    def change_pass(self, command):
        """ Change password user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for change password.")
            return

        cur_password = getpass(">> Current Password: ")
        new__password = getpass(">> New Password: ")

        if command.startswith(CMD_CHANGE_PASS_ENCRYPT):
            username = args[2]
            data = {
                'username': username,
                'cur_password': cur_password,
                'new__password': new__password
            }
            msg = make_msg_encrypt(CMD_CHANGE_PASS_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {
                'username': username,
                'cur_password': cur_password,
                'new__password': new__password
            }
            msg = make_msg(CMD_CHANGE_PASS, data)
        self._conn.sendall(msg)



class ListenThread(threading.Thread):
    """ New thread listening to server """

    def __init__(self, client):
        """ Init thread """
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        """ Run """
        while True:
            if not self.client.listen():
                break
