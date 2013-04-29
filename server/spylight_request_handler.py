#!/usr/bin/env python
# -*- coding: utf-8 -*-

from msgpack import packb as m_pack, unpackb as m_unpack
from socket import SHUT_RDWR, timeout
from SocketServer import StreamRequestHandler
from string import printable as printable_chars
from struct import pack as s_pack, unpack as s_unpack
from threading import Event, Timer
from time import sleep

from common.game_constants import MERC_TEAM, SPY_TEAM
from game_engine import GameEngine
from stoppable_thread import ThreadExit


printable_chars = set(printable_chars)


class SpylightRequestHandler(StreamRequestHandler, object):
    CONNECTION_INIT = 'CONNECTION_INIT'  # Waiting for `init` frame
    CONNECTION_RUN = 'CONNECTION_RUN'    # Waiting for all the other frames
    CONNECTION_END = 'CONNECTION_END'    # Not waiting, will send `end` frame
    CONNECTION_STOP = 'CONNECTION_STOP'  # Not waiting, will close connection

    def setup(self):
        print 'New client connected:', self.client_address[0], \
            self.client_address[1]

        super(SpylightRequestHandler, self).setup()

        self._player_id = None
        self._player_team = None

        self._sender_busy = Event()
        self._sender_interval = -1
        self._sender = None

        self.status = self.CONNECTION_INIT

        if GameEngine().all_players_connected.is_set():
            print 'Connection will be closed: game already launched (both \
teams are full)'
            self.update_status(self.CONNECTION_STOP)

    def setup_sender(self, interval):
        def _sender_action():
            self._sender = Timer(self._sender_interval, _sender_action)
            self._sender.start()

            if not self._sender_busy.is_set():
                self._sender_busy.set()
                self.sender()
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
        if self.status == self.CONNECTION_STOP:
            return
        elif status == self.CONNECTION_STOP:
            self.status = self.CONNECTION_STOP
        elif self.server.is_stopped():
            if self.status == self.CONNECTION_INIT:
                self.status = self.CONNECTION_STOP
            else:
                self.status = self.CONNECTION_END
        elif status is not None:
            self.status = status

        if self.status in (self.CONNECTION_END, self.CONNECTION_STOP):
            self.setup_sender(-1)

    def handle(self):
        try:
            self.update_status()

            while self.status not in (self.CONNECTION_END,
                                      self.CONNECTION_STOP):
                try:
                    data_size = self.rfile.read(4)
                except timeout:
                    self.update_status()
                    print self.status
                else:
                    break

            self.update_status()

            while self.status not in (self.CONNECTION_END,
                                      self.CONNECTION_STOP):
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
                        try:
                            data = self.rfile.read(data_size)
                        except timeout:
                            print 'Wrong input received: timeout'
                            self.update_status(self.CONNECTION_STOP)
                        else:
                            if len(data) < data_size:
                                print 'Wrong input received: EOF while \
waiting message content (' + str(data_size) + '\nbytes long)'
                                self.update_status(self.CONNECTION_STOP)
                            else:
                                try:
                                    data = m_unpack(data, use_list=False)
                                except Exception as exception:
                                    print 'Wrong input received:', exception
                                    self.update_status(self.CONNECTION_STOP)
                                else:
                                    self.handle_test(data)
                                    try:
                                        handler_suffix = data['type']
                                    except TypeError:
                                        print "Wrong input received: invalid \
message's type"
                                        self.update_status(self.
                                                           CONNECTION_STOP)
                                    except KeyError:
                                        print 'Wrong input received: no \
`type` field in message'
                                        self.update_status(self.
                                                           CONNECTION_STOP)
                                    else:
                                        # We must ensure that `type` field
                                        # contains a string type object
                                        if not isinstance(handler_suffix,
                                                          basestring):
                                            print 'Wrong input received: \
invalid message field `type`'
                                            self.update_status(self.
                                                               CONNECTION_STOP)
                                        else:
                                            handler_name = 'handle_' + \
                                                handler_suffix
                                            if self.status == \
                                                    self.CONNECTION_INIT and \
                                                    handler_suffix != 'init':
                                                print 'Wrong input received: \
invalid message field `type`; must be "init" during the\ninitialisation phase.'
                                                self.update_status(self.
                                                    CONNECTION_STOP)
                                            else:
                                                try:
                                                    handler = getattr(self,
                                                        handler_name)
                                                except AttributeError:
                                                    print 'Wrong input \
received: invalid message field `type`'
                                                    self.update_status(
                                                        self.CONNECTION_STOP)
                                                else:
                                                    handler(data)
                                                    while self.status not in (
                                                            self.
                                                            CONNECTION_END,
                                                            self.
                                                            CONNECTION_STOP):
                                                        try:
                                                            data_size = self.\
                                                                rfile.\
                                                                read(4)
                                                        except timeout:
                                                            self.\
                                                                update_status()
                                                        else:
                                                            break
                                                    self.update_status()

            while self.status == self.CONNECTION_END:
                sleep(1)

        except ThreadExit:
            self.update_status(self.CONNECTION_STOP)

    def handle_init(self, data):
        try:
            if not data['team'] in (MERC_TEAM, SPY_TEAM):
                print 'Wrong input received: invalid message field `team`'
                self.update_status(self.CONNECTION_STOP)
                return
            elif not set(data['nick']).issubset(printable_chars):
                print 'Wrong input received: invalid message field `nick`'
                self.update_status(self.CONNECTION_STOP)
                return
        except KeyError:
            print 'Wrong input received: missing field(s) in message of type \
`init`'
            self.update_status(self.CONNECTION_STOP)
            return

        self._player_id = GameEngine().connect_to_player(data['team'],
                                                         data['nick'])

        if self._player_id is None:
            print 'Initialisation failed: team full'
            self.update_status(self.CONNECTION_STOP)
            return

        self._player_team = data['team']

        player_state = GameEngine().get_player_state(self._player_id)
        pos_x, pos_y, max_hp = (player_state[k] for k in ('x', 'y', 'hp'))

        GameEngine().all_players_connected.wait()

        self.send({'type': 'init', 'id': self._player_id, 'pos': (pos_x,
                  pos_y), 'max_hp': max_hp, 'team': data['team'], 'map':
                  GameEngine().get_map_name(), 'map_hash': GameEngine().
                  get_map_hash(), 'players': GameEngine().get_players_info()})

        self.setup_sender(GameEngine().config.send_state_interval)
        self.update_status(self.CONNECTION_RUN)

    def handle_move(self, data):
        try:
            angle = data['d']
            speed = data['s']
            # TODO Remove the next six lines when the right type will be sent
            #      by clients
            if isinstance(angle, int):
                angle = float(angle)
            try:
                speed = float(speed)
            except ValueError:
                pass
            # TOTO -End-
            if not isinstance(angle, float) or angle < 0 or angle > 360:
                print 'Wrong input received: invalid message field `d`'
                self.update_status(self.CONNECTION_STOP)
                return
            elif not isinstance(speed, float) or speed < 0 or speed > 1:
                print 'Wrong input received: invalid message field `s`'
                self.update_status(self.CONNECTION_STOP)
                return
        except KeyError:
            print 'Wrong input received: missing field(s) in message of type \
`move`'
            self.update_status(self.CONNECTION_STOP)
            return

        GameEngine().acquire()
        GameEngine().set_movement_angle(self._player_id, angle)
        GameEngine().set_movement_speedx(self._player_id, speed)
        GameEngine().set_movement_speedy(self._player_id, speed)
        GameEngine().release()

    def handle_turn(self, data):
        try:
            angle = data['v']
            if not isinstance(angle, float) or angle < 0 or angle > 360:
                print 'Wrong input received: invalid message field `v`'
                self.update_status(self.CONNECTION_STOP)
                return
        except KeyError:
            print 'Wrong input received: missing field(s) in message of type \
`turn`'
            self.update_status(self.CONNECTION_STOP)
            return

        GameEngine().acquire()
        GameEngine().set_sight_angle(self._player_id, angle)
        GameEngine().release()

    def handle_shoot(self, data):
        print "You entered the `handle_shoot` method!"
        try:
            angle = data['v']
            if not isinstance(angle, float) or angle < 0 or angle > 360:
                print 'Wrong input received: invalid message field `v`'
                self.update_status(self.CONNECTION_STOP)
                return
        except KeyError:
            print 'Wrong input received: missing field(s) in message of type \
`shoot`'
            self.update_status(self.CONNECTION_STOP)
            return

        GameEngine().acquire()
        GameEngine().shoot(self._player_id, angle)
        GameEngine().release()

    def handle_action(self, data):
        pass

    def handle_test(self, data):
        print self.client_address[0], self.client_address[1], 'sent', data

    def send(self, message):
        try:
            data = m_pack(message)
        except Exception as exception:
            print 'Output error:', exception
        else:
            data_size = len(data)
            if data_size > 65536:
                print 'Output error: message too big to be sent'
            else:
                data_size = s_pack('!I', data_size)
                self.wfile.write(data_size + data)
                self.wfile.flush()

    def sender(self):
        self.update_status()
        if self.status == self.CONNECTION_STOP:
            return
        elif self.status == self.CONNECTION_END:
            self.send_end_stats()
            self.update_status(self.CONNECTION_STOP)
        elif self.status == self.CONNECTION_RUN:
            self.send_game_state()

    def send_game_state(self):
        GameEngine().acquire()
        s = GameEngine().get_player_state(self._player_id)
        kills = []  # TODO: Call the right GameEngine method to get the new
                    #       kills to display.
        terminals = []  # TODO: Call the right GameEngine method to get the
                        #       terminal pirating progressions.
        events = []  # TODO: Call the right GameEngine method to get the new
                     #       events.
        time = GameEngine().get_remaining_time()
        GameEngine().release()

        self.send({'type': 'update', 'l': s['hp'], 'p': (s['x'], s['y']), 'd':
                   s['d'], 's': s['s'], 'v': s['v'], 'k': kills, 'vp': s['vp'],
                   'pi': terminals, 'vo': s['vo'], 'ao': s['ao'], 'ev': events,
                   'ti': time})

    def send_end_stats(self):
        GameEngine().acquire()
        gs = GameEngine().get_game_statistics()
        ps = GameEngine().get_player_state(self._player_id)
        GameEngine().release()

        data = {'type': 'end', 'winners': gs['winners'], 'ttime': gs['ttime'],
                'lifes': ps['l']}
        if self._player_team == MERC_TEAM:
            data['kills'] = ps['kills']
        elif self._player_team == SPY_TEAM:
            data['recap'] = ps['recap']
        self.send(data)

    def finish(self):
        print 'Client disconnected:', self.client_address[0], \
            self.client_address[1]
        super(SpylightRequestHandler, self).finish()
