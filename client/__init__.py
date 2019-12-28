import socket
import threading
from cryptography.fernet import Fernet

from constant import Command
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
        self.uid = 0
        self.pkey = None
        self.listen_thread = None
        self._stop = False
        self._conn = self.get_connection()

    def get_connection(self):
        """ Arg command: connect [ip server] port [port server] """
        try:
            client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connection.connect((self.server, self.port))

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
            self._conn.send(b'')
        if self._stop:
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
            self.msg_handle(msg_recv)
        return True

    def command_handle(self, command=""):
        """ Handling all input commands """
        if command.startswith(Command.LOGIN):
            self.login(command)
        elif command.startswith(Command.REGISTER):
            self.register(command)
        elif command.startswith(Command.CHANGE_PASS):
            self.change_pass(command)
        elif command.startswith(Command.CHECK_USER):
            self.check_user(command)
        elif command.startswith(Command.SETUP_USER):
            self.setup_info(command)
        elif command.startswith(Command.DOWNLOAD):
            self.download_request(command)
        elif command.startswith(Command.UPLOAD):
            self.upload_request(command)
        elif command.startswith(Command.CHAT):
            self.chat(command)
        else:
            print(">> Undefined command.")

    def msg_handle(self, msg_recv):
        """ Handling received messages """
        from utils import decode_msg
        raw_data = decode_msg(msg_recv)
        msg_type = raw_data['type']
        response = raw_data['data']
        if msg_type == Command.LOGIN:
            self.response_login(response)
        elif msg_type.startswith(Command.DOWNLOAD):
            self.download_response(msg_type, response)
        elif msg_type.startswith(Command.UPLOAD):
            self.upload_response(msg_type, response)
        else:
            print(">> ", response['message'])

    def login(self, command):
        """ Login user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for login")
            return

        password = getpass(">> Password: ")

        if command.startswith(Command.LOGIN_ENCRYPT):
            username = args[2]
            data = {'username': username, 'password': password}
            msg = make_msg_encrypt(Command.LOGIN_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {'username': username, 'password': password}
            msg = make_msg(Command.LOGIN, data)
        self._conn.sendall(msg)

    def register(self, command):
        """ Register user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for register")
            return

        password = getpass(">> Password: ")

        if command.startswith(Command.REGISTER_ENCRYPT):
            username = args[2]
            data = {'username': username, 'password': password}
            msg = make_msg_encrypt(Command.REGISTER_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {'username': username, 'password': password}
            msg = make_msg(Command.REGISTER, data)
        self._conn.sendall(msg)

    def change_pass(self, command):
        """ Change password user """
        from getpass import getpass
        args = command.split(" ")
        if len(args) < 2:
            print("[ERROR] Username is required for change password.")
            return

        cur_password = getpass(">> Current Password: ")
        new_password = getpass(">> New Password: ")

        if command.startswith(Command.CHANGE_PASS_ENCRYPT):
            username = args[2]
            data = {
                'username': username,
                'cur_password': cur_password,
                'new_password': new_password
            }
            msg = make_msg_encrypt(Command.CHANGE_PASS_ENCRYPT, data, self.pkey)
        else:
            username = args[1]
            data = {
                'username': username,
                'cur_password': cur_password,
                'new_password': new_password
            }
            msg = make_msg(Command.CHANGE_PASS, data)
        self._conn.sendall(msg)

    def check_user(self, command):
        args = command.split(" ")
        if command.startswith(Command.CHECK_USER + ' -'):
            if len(args) < 3:
                print("[ERROR] Username is required for check_user")
                return
            msg_type = args[0] + ' ' + args[1]
            data = args[2]
        else:
            if len(args) < 2:
                print("[ERROR] Username is required for check_user")
                return
            msg_type = args[0]
            data = args[1]

        msg = make_msg(msg_type, data)
        self._conn.sendall(msg)

    def setup_info(self, command):
        """ Set up information for current user """
        args = command.split(" ")
        args_num = len(args)
        if args_num < 3:
            print(">> Missing arguments!")
            return
        username = args[args_num-1]
        if args_num > 4:
            value = ""
        else:
            value = args[2]
        if command.startswith(Command.SETUP_USER_NOTE):
            msg_type = Command.SETUP_USER_NOTE
        elif command.startswith(Command.SETUP_USER_DATE):
            msg_type = Command.SETUP_USER_DATE
        msg = make_msg(msg_type, {'username': username, 'value': value})
        self._conn.sendall(msg)

    def download_request(self, command):
        """ Make request download """
        args = command.split(" ")
        if command.startswith(Command.DOWNLOAD_ENCRYPT):
            filename = args[2]
            msg = make_msg(Command.DOWNLOAD_ENCRYPT, {'filename': filename})
        elif args[1] == '-multi_file':
            filename = []
            for index in range(2, len(args)):
                filename.append(args[index])
        else:
            filename = args[1]
        msg = make_msg(Command.DOWNLOAD, {'filename': filename})
        self._conn.send(msg)

    def download_response(self, msg_type, response):
        print(">> Starting download.")
        self._conn.send(b'ok')
        is_encrypt = False
        if msg_type == Command.DOWNLOAD_ENCRYPT:
            is_encrypt = True
        filename = response['filename']
        with open(filename, 'wb') as file:
            while True:
                raw_data = self._conn.recv(8192)
                print('receive %s' % raw_data)
                if not raw_data or raw_data == b'':
                    print("Connection to server broke.")
                    self.close_connection()
                    return
                if raw_data == b'done':
                    break
                if is_encrypt:
                    _fernet = Fernet(self.pkey)
                    data = _fernet.decrypt(raw_data)
                else:
                    data = raw_data
                file.write(data)
                self._conn.send(b'ok')
        return

    def upload_request(self, command):
        """ Make request to upload """
        args = command.split(" ")
        if command.startswith(Command.UPLOAD_ENCRYPT):
            filename = args[2]
            msg = make_msg(Command.UPLOAD_ENCRYPT, {'filename': filename})
            self._conn.send(msg)
        elif args[1] == '-multi_file':
            filename = []
            for index in range(2, len(args)):
                filename.append(args[index])
        else:
            filename = args[1]
        msg = make_msg(Command.UPLOAD, {'filename': filename})
        self._conn.send(msg)

    def upload_response(self, msg_type, response):
        is_encrypt = False
        if msg_type == Command.UPLOAD_ENCRYPT:
            is_encrypt = True
        filename = response['filename']
        file = open(filename, 'rb')
        read_stream = file.read(1024)
        while read_stream:
            if is_encrypt:
                _fernet = Fernet(self.pkey)
                send_data = _fernet.encrypt(read_stream)
            else:
                send_data = read_stream
            self._conn.send(send_data)
            print('Sent %s' % send_data)
            ack = self._conn.recv(1024)
            if ack != b'ok':
                print("Downloading error.")
                self.close_connection()
            if not ack or ack == b'':
                self.close_connection()
            read_stream = file.read(1024)
        file.close()
        self._conn.send(b'done')
        return

    def chat(self, command):
        """ Make chat terminal """

    def response_login(self, response):
        """ Handle response after login request """
        if response['code'] == 200:
            self.uid = int(response['uid'])
            print(">> ", response['message'])
        else:
            print(">> ", response['message'])

    def chat_request(self):
        """ Receive chat request from anther client """
        return


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
