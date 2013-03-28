#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SocketServer import StreamRequestHandler

from game_engine import GameEngine


class RequestHandler(StreamRequestHandler, object):
    def setup(self):
        super(RequestHandler, self).setup()
        print 'New client connected'

    def handle(self):
        while GameEngine().loop:
            data = self.rfile.readline().strip()
            print '{} a écrit :'.format(self.client_address[0])
            print data
            self.wfile.write(data.upper()+'\n')

    def finish(self):
        super(RequestHandler, self).finish()
        print 'Client disconnected'
