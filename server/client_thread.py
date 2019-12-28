""" server side """
import threading
from cryptography.fernet import Fernet

from server import LIST_CLIENTS, database as db
from constant import Command
from utils import decode_msg, decrypt_data, make_msg, make_msg_encrypt


class ClientThread(threading.Thread):
    """ Init and run thread for new connection  """

    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.uid = 0
        self.csocket = clientsocket
        self.client_address = clientAddress
        self.pkey = Fernet.generate_key()

        self.csocket.send(self.pkey)
        print("New connection added: ", clientAddress)

    def close_connection(self):
        """ Handle connection close """
        print("Client at ", self.client_address, " disconnected...")
        self.csocket.close()
        LIST_CLIENTS.remove({'sock': self.csocket, 'uid': self.uid})

    def run(self):
        while True:
            msg_recv = self.csocket.recv(8192)
            if msg_recv == b'':
                break
            self.msg_handle(msg_recv)
        self.close_connection()

    def msg_handle(self, msg_recv):
        """ Handling received messages """
        msg = decode_msg(msg_recv)
        msg_type = msg['type']
        raw_data = msg['data']
        if msg_type == Command.LOGIN:
            self.login(raw_data)
        elif msg_type == Command.LOGIN_ENCRYPT:
            decrypted = decrypt_data(raw_data, self.pkey)
            self.login(decrypted)
        elif msg_type == Command.REGISTER:
            self.register(raw_data)
        elif msg_type == Command.REGISTER_ENCRYPT:
            decrypted = decrypt_data(raw_data, self.pkey)
            self.register(decrypted)
        elif msg_type == Command.CHANGE_PASS:
            self.change_pass(raw_data)
        elif msg_type == Command.CHANGE_PASS_ENCRYPT:
            decrypted = decrypt_data(raw_data, self.pkey)
            self.change_pass(decrypted)
        elif msg_type in (Command.CHECK_USER, Command.CHECK_USER_ONL):
            self.check_user_online(raw_data)
        elif msg_type.startswith(Command.CHECK_USER):
            self.check_user(msg_type, raw_data)
        elif msg_type.startswith(Command.SETUP_USER):
            self.setup_user(msg_type, raw_data)
        elif msg_type.startswith(Command.DOWNLOAD):
            self.download(msg_type, raw_data)
        elif msg_type.startswith(Command.UPLOAD):
            self.upload(msg_type, raw_data)

    def login(self, data):
        """ call db to verify password """
        user_id = db.login_user(data['username'], data['password'])
        if user_id == 0:
            response = make_msg(Command.LOGIN, {'code': 400, 'message': 'Login unsuccessfully.'})
        else:
            for client in LIST_CLIENTS:
                if client['sock'] == self.csocket:
                    client['uid'] = user_id
                    self.uid = user_id
                    break
            response = make_msg(
                Command.LOGIN,
                {'code': 200, 'message': 'Login successfully.', 'uid': user_id})
        self.csocket.send(response)

    def register(self, data):
        """ call db to insert user """
        user_id = db.insert_user(data['username'], data['password'])
        if user_id == 0:
            message = "Username '%s' exited." % data['username']
            response = make_msg(Command.REGISTER, {'code': 400, 'message': message})
        else:
            response = make_msg(Command.REGISTER, {'code': 200, 'message': 'Register success.'})
        self.csocket.send(response)

    def change_pass(self, data):
        """ call db to update password"""
        result = db.change_password(data['username'], data['cur_password'], data['new_password'])
        if not result:
            message = "Current password is not match."
            response = make_msg(Command.CHANGE_PASS, {'code': 400, 'message': message})
        else:
            response = make_msg(Command.CHANGE_PASS, {'code': 200, 'message': 'Change pass success.'})
        self.csocket.send(response)

    def check_user(self, msg_type, data):
        """ call db to get user information """
        result = db.get_user_info(username=data)
        # result = [id, name, date, note]
        if result:
            if msg_type == Command.CHECK_USER_DATE:
                message = "Birthdate of %s is: %s." % (data, result[2])
            elif msg_type == Command.CHECK_USER_NAME:
                message = "Name of %s is: %s." % (data, data)
            elif msg_type == Command.CHECK_USER_NOTE:
                message = "Note of %s is: '%s'." % (data, result[3])
            elif msg_type == Command.CHECK_USER_SHOW:
                message = "ID: %s, " % result[0]
                message += "Name: %s, " % result[1]
                message += "Date: %s, " % result[2]
                message += "Note: %s" % result[3]
            response = make_msg(Command.CHECK_USER, {'code': 200, 'message': message})
        else:
            message = "User %s does not exit." % data
            response = make_msg(Command.CHECK_USER, {'code': 400, 'message': message})
        self.csocket.send(response)

    def check_user_online(self, data):
        """ call db to get user information """
        result = db.get_user_info(username=data)
        if result:
            message = ""
            for client in LIST_CLIENTS:
                if client['uid'] == result[0]:
                    message = "User %s is online." % data
                    break
            if message == "":
                message = "User %s is offline." % data
            response = make_msg(Command.CHECK_USER_ONL, {'code': 200, 'message': message})
        else:
            message = "User %s does not exist." % data
            response = make_msg(Command.CHECK_USER_ONL, {'code': 400, 'message': message})
        self.csocket.send(response)

    def setup_user(self, msg_type, data):
        """ Setting user info """
        username = data['username']
        value = data['value']
        query = db.get_user_info(username=username)
        if not query:
            message = "User %s does not exist." % username
            response = make_msg(Command.SETUP_USER, {'code': 400, 'message': message})
        elif msg_type == Command.SETUP_USER_NOTE:
            db.update_user_info(query[0], 'note', value)
            response = make_msg(Command.CHECK_USER, {'code': 200, 'message': 'ok'})
        elif msg_type == Command.SETUP_USER_DATE:
            db.update_user_info(query[0], 'date', value)
            response = make_msg(Command.CHECK_USER, {'code': 200, 'message': 'ok'})
        self.csocket.send(response)

    def upload(self, msg_type, data):
        """ Upload file from client to server """
        is_encrypt = False
        print(">> Starting download.")
        file_lists = data['filename']
        if not isinstance(file_lists, list):
            file_lists = [file_lists]
        for filename in file_lists:
            if msg_type == Command.UPLOAD_ENCRYPT:
                is_encrypt = True
                self.csocket.send(make_msg(Command.UPLOAD_ENCRYPT, {'filename': filename}))
            else:
                self.csocket.send(make_msg(Command.UPLOAD, {'filename': filename}))
            with open(filename, 'wb') as file:
                while True:
                    receive = self.csocket.recv(8192)
                    print('receive %s' % receive)
                    if not receive or receive == b'':
                        print("Connection to server broke.")
                        self.close_connection()
                        return
                    if receive == b'done':
                        break
                    if is_encrypt:
                        _fernet = Fernet(self.pkey)
                        write_input = _fernet.decrypt(receive)
                    else:
                        write_input = receive
                    file.write(write_input)
                    self.csocket.send(b'ok')
        return

    def download(self, msg_type, data):
        """ Client request download a file """
        is_encrypt = False
        file_lists = data['filename']
        if not isinstance(file_lists, list):
            file_lists = [file_lists]
        for filename in file_lists:
            if msg_type == Command.DOWNLOAD_ENCRYPT:
                is_encrypt = True
                self.csocket.send(make_msg(Command.DOWNLOAD_ENCRYPT, {'filename': filename}))
            else:
                self.csocket.send(make_msg(Command.DOWNLOAD, {'filename': filename}))
            file = open(filename, 'rb')
            read_stream = file.read(1024)
            ack = self.csocket.recv(1024)
            if not ack or ack == b'':
                self.close_connection()
            if ack != b'ok':
                print(ack)
                print("Downloading error.")
                self.close_connection()
            while read_stream:
                if is_encrypt:
                    _fernet = Fernet(self.pkey)
                    msg_send = _fernet.encrypt(read_stream)
                else:
                    msg_send = read_stream
                self.csocket.send(msg_send)
                print('Sent %s' % msg_send)
                ack = self.csocket.recv(1024)
                if not ack or ack == b'':
                    self.close_connection()
                if ack != b'ok':
                    print(ack)
                    print("Downloading error.")
                    self.close_connection()
                read_stream = file.read(1024)
            file.close()
            self.csocket.send(b'done')
        return
