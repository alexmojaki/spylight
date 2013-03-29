#!/usr/bin/python
import sys
from time import sleep
import logging

import socket
import threading
import struct
import msgpack

from kivy.logger import Logger


class NetworkInterface(object):
    """docstring for NetworkInterface"""

    def __init__(self, hostname, port, on_message_recieved=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((hostname, port))

        if on_message_recieved:
            self.on_message_recieved = on_message_recieved

        t = threading.Thread(target=self._receive_forever)
        t.daemon = True  # helpful if you want it to die automatically
        t.start()

    def send(self, message):
        msglen = len(message)
        Logger.debug('SL|NetworkInterface: Sending message (%d): %s', msglen, message)
        self._socket.send(struct.pack('!i', msglen))
        totalsent = 0
        while totalsent < msglen:
            sent = self._socket.send(message[totalsent:])
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
