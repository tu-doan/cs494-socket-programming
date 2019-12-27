""" server side """
import threading
from cryptography.fernet import Fernet

from utils import make_msg


class ClientThread(threading.Thread):
    """ Init and run thread for new connection  """

    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.client_address = clientAddress
        self.pkey = Fernet.generate_key()

        self.csocket.send(self.pkey)
        print("New connection added: ", clientAddress)

    def run(self):
        msg = ''
        while True:
            data = self.csocket.recv(8196)
            if data == b'':
                break
            msg = data.decode()
            if msg == 'bye':
                break
            print("from client: ", msg)
        print("Client at ", self.client_address, " disconnected...")
        self.csocket.close()
