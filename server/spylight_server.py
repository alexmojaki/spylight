#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from time import sleep

from game_engine import GameEngine
from spylight_request_handler import SpylightRequestHandler
from threading_tcp_server import ThreadingTCPServer


class SpylightServer(object):
    def __init__(self, host, port, map_file, config_file='spylight.cfg'):
        self.init_game_engine(config_file, map_file)
        self.init_tcp_server(host, port)

    def init_game_engine(self, config_file, map_file):
        GameEngine().init(config_file, map_file)

    def init_tcp_server(self, host, port):
        self._tcp_server = ThreadingTCPServer((host, port),
                                              SpylightRequestHandler)
        self._tcp_server.serve_forever(start=False)

    def start(self):
        print 'Starting server...'

        GameEngine().start()
        self._tcp_server.handler_thread.start()

        self.run()

    def run(self):
        force = False

        while GameEngine().loop:
            try:
                # We should do something clever here.
                sleep(10)
            except KeyboardInterrupt:
                force = True
                break

        self.shutdown(force)

    def shutdown(self, force=False):
        print 'Shutting down server{}...'.format(' (the hardcore way)' if
                                                 force else '')

        self._tcp_server.shutdown()
        self._tcp_server.handler_thread.stop(force)
        self._tcp_server.handler_thread.join()
        GameEngine().shutdown(force)


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print 'usage: {} host port'.format(sys.argv[0])
        sys.exit(1)

    SpylightServer(sys.argv[1], int(sys.argv[2]), '').start()
