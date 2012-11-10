#!/usr/bin/python
import socket
import sys

class ClientNetworker(object):
    """docstring for ClientNetworker"""
    OBJECT_TXT = "\nd "
    SHOOT_TXT = "\nsh "
    ACTIVATE_TXT = "\nd "
    SPY_TXT = "s" # no new line there, first line of the msg
    MERCERNARY_TXT = "m" # no new line there, first line of the msg
    SPY_TYPE = 1
    MERCENARY_TYPE = 2
    MSG_END = "\n\n"
    
    def __init__(self, playerType):
        super(ClientNetworker, self).__init__()
        if playerType == SPY_TYPE:
            self.data = self.SPY_TXT
        elif playerType == MERCENARY_TYPE:
            self.data = self.MERCERNARY_TXT

    def object(self, id):
        self.data += self.OBJECT_TXT + str(id)

    def shoot(self):
        self.data += self.SHOOT_TXT

    def activate(self):
        self.data += self.ACTIVATE_TXT

    def connect(self, host, port):
        self.s = sock.connect((host, port))
    def send(self):
        self.s.sendall(data + self.MSG_END)


if sys.argv[0] is not None:
        PORT = int(sys.argv[0])
    if PORT is None or PORT < 0:
        PORT = 9999
    
    HOST = "localhost"
data = " ".join(sys.argv[2:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    while True:
        sock.sendall(data + "\n")
        # Receive data from the server and shut down
        received = sock.recv(1024)
        print "Sent: {}".format(data)
        print "Rcv: {}".format(received)
finally:
    sock.close()
