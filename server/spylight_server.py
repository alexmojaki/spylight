#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from game_engine import GameEngine
from spylight_request_handler import SpylightRequestHandler
from threading_tcp_server import ThreadingTCPServer


class SpylightServer(object):
    def __init__(self):
        print 'Welcome to Spylight!'
        self.init_game_engine(config_file='server/spylight.cfg')
        self.init_tcp_server(GameEngine().config.server_host,
                             GameEngine().config.server_port)

    def init_game_engine(self, config_file):
        print 'Loading game engine...'
        GameEngine().init(config_file)

    def init_tcp_server(self, host, port):
        print 'Starting TCP server...'
        self._tcp_server = ThreadingTCPServer((host, port),
                                              SpylightRequestHandler,
                                              reuse_address=True)

    def start(self):
        self._tcp_server.serve_forever()
        self.run()

    def run(self):
        force = False
        sleep_time = GameEngine().config.end_game_poll_time

        try:
            while GameEngine().loop:
                sleep(sleep_time)
        except KeyboardInterrupt:
            force = True

        self.shutdown(force)

    def shutdown(self, force=False):
        print 'Shutting down server{}...'.format(' (the hardcore way)' if
                                                 force else '')

        GameEngine().end_of_game()
        self._tcp_server.shutdown(force)
        GameEngine().stop_auto_mode(force)
        print 'Good bye.'

if __name__ == '__main__':
    SpylightServer().start()
