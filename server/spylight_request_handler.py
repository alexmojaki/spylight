#!/usr/bin/env python
# -*- coding: utf-8 -*-

from msgpack import unpackb as m_unpack
from SocketServer import StreamRequestHandler
from struct import unpack as s_unpack
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
                data_size = self.rfile.read(4)
                if len(data_size) < 4:
                    print 'Wrong input received: EOF while waiting for \
message length (4 bytes long)'
                    continue  # Discard the received bytes and start again
                data = m_unpack(self.rfile.read(s_unpack('!I', data_size)[0]))
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
