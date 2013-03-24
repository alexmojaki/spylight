#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GameEngine:
    def __init__(self, config_file, map_file):
        self.load_config(config_file)
        self.load_map(map_file)

    def load_config(self, config_file):
        pass

    def load_map(self, map_file):
        self._player_number = 4

    def get_nb_players(self):
        return self._player_number
