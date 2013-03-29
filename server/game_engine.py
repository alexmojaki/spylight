#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event

from config_handler import ConfigHandler

class Player(object):
    """Player class, mainly POCO object"""
    def __init__(self, player_id):
        super(Player, self).__init__()
        self.player_id = player_id
        

class GameEngine(object):
    _instances = {}
    players = None

    def __new__(cls, *args, **kargs):
        if GameEngine._instances.get(cls) is None:
            GameEngine._instances[cls] = object.__new__(cls, *args, **kargs)
        return GameEngine._instances[cls]

    def init(self, config_file, map_file):
        self._loop = Event()

        self.load_config(config_file)
        self.load_map(map_file)

    @property
    def loop(self):
        return not self._loop.is_set()

    def load_config(self, config_file):
        self.config = ConfigHandler(config_file)
        self._player_number = 4  # TODO: Update with the true player number
                                 #       read from the map file.
        # Loading players
        self._players = [Player(i) for i in xrange(0, self._player_number)]

    def load_map(self, map_file):

    def get_nb_players(self):
        return self._player_number

    def start(self):
        self._loop.clear()

    def updateMovementDir(self, pid, angle):
        self._players[pid].movAngle = angle

    def shutdown(self, force=False):
        self._loop.set()
