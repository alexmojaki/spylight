#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SocketServer import StreamRequestHandler
from threading import Event, Timer

from game_engine import GameEngine
from stoppable_thread import ThreadExit


class SpylightRequestHandler(StreamRequestHandler, object):
    def setup(self):
        print 'New client connected'
        super(SpylightRequestHandler, self).setup()
        self.writer_busy = Event()
        self.writer = Timer(GameEngine().config.send_state_interval, self.
                            send_game_state)
        self.writer.start()

    def handle(self):
        try:
            while not self.server.handler_thread.is_stopped():
                data = self.rfile.readline().strip()
                print '{} a écrit :'.format(self.client_address[0])
                print data
        except ThreadExit:
            return

    def send_game_state(self):
        self.writer = Timer(GameEngine().config.send_state_interval, self.
                            send_game_state)
        self.writer.start()
        if not self.server.handler_thread.is_stopped():
            if not self.writer_busy.is_set():
                self.writer_busy.set()

                self.wfile.write('Plop!\n')

                self.writer_busy.clear()
        else:
            self.writer.cancel()

    def finish(self):
        print 'Client disconnected'
        super(SpylightRequestHandler, self).finish()
