#!/usr/bin/env python
# -*- coding: utf-8 -*-

from game_engine import GameEngine
from SocketServer import ThreadingMixIn, TCPServer
from threading import Thread, Event

from stoppable_thread import StoppableThread


class ThreadingTCPServer(ThreadingMixIn, TCPServer, object):
    def __init__(self, address, request_handler, reuse_address=False):
        self.allow_reuse_address = reuse_address
        super(ThreadingTCPServer, self).__init__(address, request_handler)
        self._stopped = Event()
        self._server_thread = None
        self._handler_threads = {}
        print 'TCP server waiting for connections on {}, port {}.'.format(
            *address)

    def get_request(self):
        sock, addr = super(ThreadingTCPServer, self).get_request()
        sock.settimeout(GameEngine().config.handle_timeout)
        return sock, addr

    def process_request(self, request, client_address):
        try:
            self._handler_threads[client_address]
        except KeyError:
            pass
        else:
            print 'Connection error: a connection from', client_address[0]
            print '                  with source port', client_address[1],
            'is already open.'
            return

        t = StoppableThread(target = self.process_request_thread, args = (
            request, client_address))
        self._handler_threads[client_address] = t
        t.daemon = self.daemon_threads
        t.start()

    def serve_forever(self):
        self._server_thread = Thread(target=super(ThreadingTCPServer, self).
                                     serve_forever)
        self._stopped.clear()
        self._server_thread.start()

    def shutdown(self, force=False):
        self._stopped.set()
        super(ThreadingTCPServer, self).shutdown()

        for t in self._handler_threads.values():
            t.stop(force)
        for t in self._handler_threads.values():
            t.join()
        self._server_thread.join()

    def is_stopped(self):
        return self._stopped.is_set()
