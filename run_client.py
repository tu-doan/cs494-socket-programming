""" This is clientside command """
from client import Client


print(">>>Connect to server by typing: connect [server] port [port]\n>>>Disconnect by typing: close")
command = input()
args = command.split(" ")

if (args[0].lower() == "connect"):
    server = args[1] if len(args) > 1 else "127.0.0.1"
    port = int(args[3] if len(args) > 3 else "8080")
    CLIENT = Client(server, port)
