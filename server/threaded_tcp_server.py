#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from SocketServer import ThreadingMixIn, TCPServer


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def set_client_number(self, client_number):
        self._client_number = client_number

    def threaded_serve_forever(self):
        thread = Thread(target=self.serve_forever)
        thread.start()
        return thread
