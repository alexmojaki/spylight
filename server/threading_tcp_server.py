#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SocketServer import ThreadingMixIn, TCPServer

from stoppable_thread import StoppableThread


class ThreadingTCPServer(ThreadingMixIn, TCPServer, object):
    def __init__(self, address, request_handler, reuse_address=False):
        self.allow_reuse_address = reuse_address
        super(ThreadingTCPServer, self).__init__(address, request_handler)
        self.server_thread = None

    def serve_forever(self, start=True):
        self.handler_thread = StoppableThread(target=super(ThreadingTCPServer,
                                                           self).serve_forever)
        if start:
            self.handler_thread.start()
