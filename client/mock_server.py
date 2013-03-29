#!/usr/bin/python

import socket
import struct
import threading
import math
import msgpack


msg_template = '{{ "l": 0, "p": {pos}, "d": 0, "s": 0, "v": 0, "k": 0, "vp": 0, "pi": 0, "vo": 0, "ao": 0, "ev": 0, "ti": 0 }}'


def run_server():
    mastersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # mastersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mastersocket.bind(('localhost', 9999))
    mastersocket.listen(1)

    (clientsocket, address) = mastersocket.accept()
    game = GameMock(clientsocket)

    t = threading.Thread(target=game._receive_forever)
    t.daemon = True  # helpful if you want it to die automatically
    t.start()
    while 1:
        msg = raw_input("> ")
        mysend(clientsocket, msg)
        pass


class GameMock(object):
    def __init__(self, socket):
        self._socket = socket
        self.charpos = [100, 200]

        init_info = myreceive(socket)
        mysend(socket, {
            'team': init_info['team'],
            'id': 0,
            'pos': self.charpos,
            'players': [],
            'map': 'test.hfm',
            'map_hash': 'bleh'
        })

    def _receive_forever(self):
        while 1:
            msg = myreceive(self._socket)
            self.update_pos(msg)
        print 'fin'

    def update_pos(self, msg):
        direction = float(msg['d'])
        print direction
        speed = float(msg['s'])
        dx = -math.sin(math.radians(direction)) * speed
        dy = math.cos(math.radians(direction)) * speed
        print dx, dy
        self.charpos = [self.charpos[0] + dx, self.charpos[1] + dy]
        print self.charpos
        msg = msg_template.format(pos=self.charpos)
        mysend(self._socket, msg)


def mysend(socket, msg):
    msg = msgpack.packb(msg)
    msglen = len(msg)
    print 'msglen:', msglen
    msglenb = struct.pack('!i', msglen)
    socket.send(msglenb)
    totalsent = 0
    print msg
    while totalsent < msglen:
        sent = socket.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


def myreceive(socket):
    msg_len = struct.unpack('!i', socket.recv(4))[0]
    msg = socket.recv(int(msg_len))
    msg = msgpack.unpackb(msg)

    # msg = ''
    # while len(msg) < msglen:
    #     chunk = socket.recv(msglen-len(msg))
    #     if chunk == '':
    #         raise RuntimeError("socket connection broken")
    #     msg = msg + chunk
    print msg
    return msg


if __name__ == '__main__':
    run_server()
