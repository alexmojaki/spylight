#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from game_engine import GameEngine
from spylight_request_handler import SpylightRequestHandler
from threading_tcp_server import ThreadingTCPServer


class SpylightServer(object):
    def __init__(self):
        self.init_game_engine(config_file='server/spylight.cfg')
        self.init_tcp_server(GameEngine().config.server_host,
                             GameEngine().config.server_port)

    def init_game_engine(self, config_file):
        GameEngine().init(config_file)

    def init_tcp_server(self, host, port):
        self._tcp_server = ThreadingTCPServer((host, port),
                                              SpylightRequestHandler, reuse_address=True)
        self._tcp_server.serve_forever(start=False)

    def start(self):
        print 'Starting server...'

        self._tcp_server.handler_thread.start()
        self.run()

    def run(self):
        force = False

        try:
            while GameEngine().loop:
                sleep(1)
        except KeyboardInterrupt:
            force = True

        self.shutdown(force)

    def shutdown(self, force=False):
        print 'Shutting down server{}...'.format(' (the hardcore way)' if
                                                 force else '')

        self._tcp_server.shutdown()
        self._tcp_server.handler_thread.stop(force)
        self._tcp_server.handler_thread.join()
        GameEngine().shutdown(force)

if __name__ == '__main__':
    SpylightServer().start()
