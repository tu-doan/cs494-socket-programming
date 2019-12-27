import socket
import threading

from client import function


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
            print("Connect successful to %s:%s" % (self.server, self.port))
            client_connection.sendall(bytes("I want to connect.", 'UTF-8'))

            # first receive message is private key
            msg_recv = self._conn.recv(8192)
            from utils import decode_msg
            raw_data = decode_msg(msg_recv)
            if raw_data['type'] != "nothing":
                raise Exception("Error")
            self.pkey = raw_data['data']
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
        if command.startswith("login"):
            function.login(self._conn, command)

    def msg_handle(self, msg_recv):
        """ Handling received messages """
        from utils import decode_msg
        raw_data = decode_msg(msg_recv)
        msg_type = raw_data['type']
        msg_data = raw_data['data']
        print(msg_type, msg_data)


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
