import socket
import struct


def run_server():
    mastersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mastersocket.bind(('localhost', 9999))
    mastersocket.listen(1)

    while 1:
        (clientsocket, address) = mastersocket.accept()
        while 1:
            msg = raw_input("> ")
            mysend(clientsocket, msg)


def mysend(socket, msg):
    msglen = len(msg)
    socket.send(struct.pack('i', msglen))
    totalsent = 0
    while totalsent < msglen:
        sent = socket.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


def myreceive(socket, msglen):
    msg = ''
    while len(msg) < msglen:
        chunk = socket.recv(msglen-len(msg))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        msg = msg + chunk
    return msg


if __name__ == '__main__':
    run_server()
