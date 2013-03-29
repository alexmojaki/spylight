#!/usr/bin/python

import socket
import threading
import struct
import msgpack

from kivy.logger import Logger


class NetworkInterface(object):
    """docstring for NetworkInterface"""

    def __init__(self, hostname, port, on_message_recieved=None):
        self._hostname = hostname
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_message_recieved = on_message_recieved

    def connect(self, init_message):
        self._socket.connect((self._hostname, self._port))
        self.send(init_message)
        return self.receive()

    def ready(self):
        # @TODO: send ready message?

        t = threading.Thread(target=self._receive_forever)
        t.daemon = True  # helpful if you want it to die automatically
        t.start()

    def send(self, message):
        bmessage = msgpack.packb(message)
        msglen = len(bmessage)
        Logger.debug('SL|NetworkInterface: Sending message (%d): %s', msglen, message)
        self._socket.send(struct.pack('!i', msglen))
        totalsent = 0
        while totalsent < msglen:
            sent = self._socket.send(bmessage[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def _receive_forever(self):
        while 1:
            msg = self.receive()
            if self.on_message_recieved:
                self.on_message_recieved(msg)
        print 'fin'

    def receive(self):
        msg_len = struct.unpack('!i', self._socket.recv(4))[0]
        data = self._socket.recv(int(msg_len))
        return msgpack.unpackb(data)
