""" Function to handle command """
from utils import make_msg


def login(client_conn, command):
    """ Login user """
    from getpass import getpass
    args = command.split(" ")
    if len(args) < 2:
        print("[ERROR] Username is required for login")
        return
    username = args[1]
    password = getpass(">> Password: ")
    data = [username, password]
    msg = make_msg("login", data)
    client_conn.sendall(msg)
