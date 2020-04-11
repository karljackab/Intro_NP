import socket
import process
import copy
import utils
import threading
import sys


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = '127.0.0.1'
port = int(sys.argv[1])
s.bind((host, port))

s.listen(10)
print(f'Server is running at {host}:{port}')

connection = utils.Connection()
# db = utils.DB()


while True:
    c, addr = s.accept()
    c_id = connection.add(c, addr)

    child = threading.Thread(target=process.main, args=(connection, c_id))
    child.start()