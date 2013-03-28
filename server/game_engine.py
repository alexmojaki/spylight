#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event

from config_handler import ConfigHandler


class GameEngine(object):
    _instances = {}

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

    def load_map(self, map_file):
        self._player_number = 4  # TODO: Update with the true player number
                                 #       read from the map file.

    def get_nb_players(self):
        return self._player_number

    def start(self):
        self._loop.clear()

    def shutdown(self, force=False):
        self._loop.set()
