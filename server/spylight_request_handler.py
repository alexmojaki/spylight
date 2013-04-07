#!/usr/bin/env python
# -*- coding: utf-8 -*-

from msgpack import unpackb as m_unpack
from SocketServer import StreamRequestHandler
from struct import unpack as s_unpack
from threading import Event, Timer

from game_engine import GameEngine
from stoppable_thread import ThreadExit


class SpylightRequestHandler(StreamRequestHandler, object):
    CONNECTION_INIT = 'CONNECTION_INIT'
    CONNECTION_RUN = 'CONNECTION_RUN'
    CONNECTION_STOP = 'CONNECTION_STOP'

    def setup(self):
        print 'New client connected:', self.client_address[0], \
            self.client_address[1]
        super(SpylightRequestHandler, self).setup()

        self._sender_busy = Event()
        self._sender_interval = -1
        self._sender = None

        self._status = self.CONNECTION_INIT

    def setup_sender(self, interval):
        def _sender_action():
            self._sender = Timer(self._sender_interval, _sender_action)
            self._sender.start()

            if not self._sender_busy.is_set():
                self._sender_busy.set()
                self.send()
                self._sender_busy.clear()

        if self._sender is not None:
            self._sender.cancel()
            self._sender_interval = -1
            self._sender = None

        if interval > 0:
            self._sender_interval = interval
            self._sender = Timer(interval, _sender_action)
            self._sender.start()

    def update_status(self, status=None):
        if self.server.handler_thread.is_stopped():
            self._status = self.CONNECTION_STOP
        elif status is not None:
            self._status = status

        if self._status == self.CONNECTION_STOP:
            self.setup_sender(-1)

    def handle(self):
        try:
            while self._status != self.CONNECTION_STOP:
                data_size = self.rfile.read(4)
                if len(data_size) < 4:
                    print 'Wrong input received: EOF while waiting for \
message length (4 bytes long)'
                    self.update_status(self.CONNECTION_STOP)
                else:
                    data_size = s_unpack('!I', data_size)[0]
                    if data_size > 4096:
                        print 'Wrong input received: message size exceeds \
4096 bytes'
                        self.update_status(self.CONNECTION_STOP)
                    else:
                        data = self.rfile.read(data_size)
                        if len(data) < data_size:
                            print 'Wrong input received: EOF while waiting \
message content (' + str(data_size) + '\nbytes long)'
                            self.update_status(self.CONNECTION_STOP)
                        else:
                            try:
                                data = m_unpack(data)
                            except Exception as exception:
                                print 'Wrong input received:', exception
                                self.update_status(self.CONNECTION_STOP)
                            else:
                                try:
                                    handler_suffix = data['type']
                                except TypeError:
                                    print "Wrong input received: invalid \
message's type"
                                    self.update_status(self.CONNECTION_STOP)
                                except KeyError:
                                    print 'Wrong input received: no `type` \
field in message'
                                    self.update_status(self.CONNECTION_STOP)
                                    self._handle_print(data)
                                else:
                                    # We must ensure that `type` field contains
                                    # a string type object
                                    if not isinstance(handler_suffix,
                                                      basestring):
                                        print 'Wrong input received: invalid \
message field `type`'
                                        self.update_status(self.
                                                           CONNECTION_STOP)
                                    else:
                                        handler_name = 'handle_' + \
                                            handler_suffix
                                        if self._status == \
                                                self.CONNECTION_INIT and \
                                                handler_suffix != 'init':
                                            print 'Wrong input received: \
invalid message field `type`; must be "init" during the\ninitialisation phase.'
                                            self.update_status(self.
                                                               CONNECTION_STOP)
                                        else:
                                            try:
                                                getattr(self, handler_name)(
                                                    data)
                                            except AttributeError:
                                                print 'Wrong input received: \
invalid message field `type`'
                                                self.update_status(self.
                                                    CONNECTION_STOP)
                                                self._handle_print(data)
                                            else:
                                                self.update_status()
        except ThreadExit:
            self.update_status(self.CONNECTION_STOP)

    def handle_init(self, data):
        pass

    def _handle_print(self, data):
        print data

    def handle_test(self, data):
        print 'Test message received:', data

    def send(self):
        self.send_game_state()

    def send_game_state(self):
        self.wfile.write('Plop!\n')

    def finish(self):
        print 'Client disconnected'
        super(SpylightRequestHandler, self).finish()
