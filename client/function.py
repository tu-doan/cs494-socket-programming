from utils import make_msg, decode_msg

def login(client_conn, command):
    """ Login user """
    args = command.split(" ")
    if len(args) < 2:
        print("[ERROR] Username is required for login")
        return
    username = args[1]
    from getpass import getpass
    password = getpass(">> Password: ")
    data = [username, password]
    msg = make_msg("login", data)
    # client_conn.sendall(msg)
