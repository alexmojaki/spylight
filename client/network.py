#!/usr/bin/python

import socket
import threading
import struct
import msgpack

from kivy.logger import Logger


class MessageFactory(object):

    @staticmethod
    def init(team, nick):
        return {'type': 'init', 'team': team, 'nick': nick}

    @staticmethod
    def move(direction, speed):
        return {'type': 'move', 'd': direction, 's': speed}

    @staticmethod
    def turn(angle):
        return {'type': 'turn', 'v': angle}

    @staticmethod
    def shoot(angle):
        return {'type': 'shoot', 'v': angle}

    @staticmethod
    def action(keydown):
        return {'type': 'action'}

    @staticmethod
    def update(team, nick):
        pass


class NetworkInterface(object):
    """docstring for NetworkInterface"""

    def __init__(self, hostname, port, on_message_recieved=None):
        self._hostname = hostname
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_message_recieved = on_message_recieved
        self._connected = False

    def connect(self, init_message):
        self._socket.connect((self._hostname, self._port))
        self._connected = True
        self.send(init_message)
        return self.receive()

    def disconnect(self):
        Logger.info('SL|NetworkInterface: Disconnecting.')
        self._connected = False
        self._socket.close()

    def ready(self):
        t = threading.Thread(target=self._receive_forever)
        t.daemon = True  # helpful if you want it to die automatically
        t.start()

    def send(self, message):
        if self._connected:
            bmessage = msgpack.packb(message)
            msglen = len(bmessage)
            Logger.debug('SL|NetworkInterface: Sending message (%d): %s',
                         msglen, message)
            self._socket.send(struct.pack('!i', msglen))
            totalsent = 0
            while totalsent < msglen:
                sent = self._socket.send(bmessage[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent

    def _receive_forever(self):
        while self._connected:
            msg = self.receive()
            if self.on_message_recieved:
                self.on_message_recieved(msg)

    def receive(self):
        msg_len = struct.unpack('!i', self._socket.recv(4))[0]
        data = self._socket.recv(int(msg_len))
        data = msgpack.unpackb(data)
        Logger.debug('SL|NetworkInterface: Message recieved: %s', data)
        return data
