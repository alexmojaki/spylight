# -*- coding: utf-8 -*-

import sys

# Colored logs. the text before the first ':' will be used as log tag
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from common.map_parser import SpyLightMap
from client.network import NetworkInterface, MessageFactory
from client.character import Character, Replica
from client.hud import SpylightHUD
from client.map_view import MapView
from client.input import KeyboardManager, TouchManager
from client.action import ActionManager
from client import utils


class GameScreen(Screen):
    def __init__(self, serverip, serverport, team, nick, **kwargs):
        Builder.load_file(utils.kvPath.format('game_screen'))
        super(GameScreen, self).__init__(**kwargs)  # init with the name

        # Declared here to be able to handle screen changes
        self.km = KeyboardManager()
        self.km.bind(quit=self.goToPauseScreen)
        self.tm = TouchManager()

        game = SpylightGame(serverip, serverport, team, nick, self.km, self.tm)
        self.add_widget(game)

    def goToPauseScreen(self, instance, value):
        if not value:  # False means key up event
            Logger.info('SL|GameScreen: TODO: Pause Screen')


class SpylightGame(Widget):

    def __init__(self, serverip, serverport, team, nick, keyboardMgr, touchMgr):
        super(SpylightGame, self).__init__()

        # Register to the server
        self._ni = NetworkInterface(serverip, serverport)
        init_response = self._ni.connect(MessageFactory.init(team, nick))

        # Parse server init message
        self.team = init_response['team']
        self.playerid = init_response['id']

        # Init environment
        loaded_map = SpyLightMap(init_response['map'])
        Logger.info("SL|SLGame: Map loaded: %s", loaded_map.title)
        Logger.info("SL|SLGame: Map size: %s", loaded_map.size)

        if init_response['map_hash'] != loaded_map.get_hash():
            Logger.error("SL|SLGame: Wrong map hash. Expected %s",
                         loaded_map.get_hash())
            sys.exit()

        self.init_game_view(loaded_map, init_response)

        self.hud = SpylightHUD(self, max_hp=init_response['max_hp'])
        self.add_widget(self.hud)

        # Register input listeners
        self.am = ActionManager(self._ni, keyboardMgr, touchMgr, self)

        # Game client ready
        self._ni.on_message_recieved = self.update
        self._ni.ready()

    def init_game_view(self, loaded_map, init_response):
        self.players = {}  # Player replicas.
        for player in init_response['players']:
            if player[1] == init_response['id']:  # Local player
                self.char = Character(nick=player[0], playerid=player[1],
                                      team=player[2])
                self.players[player[1]] = self.char
            else:
                self.players[player[1]] = Replica(nick=player[0],
                                                  playerid=player[1],
                                                  team=player[2],
                                                  pos=(200, 200))

        self.mv = MapView(loaded_map, self.char, self.players)
        self.add_widget(self.mv)

        self.add_widget(self.char)  # after the map to keep it always visible!
        self.char.bind(offset=self.mv.update_pos)
        self.char.set_game_pos(init_response['pos'])  # Also updates the map

    def update(self, data):
        Logger.debug('SL|SLGame: update parameter: %s', data)
        self.char.update(data)
        self.hud.update(data)

        player_updates = {}
        for vp in data['vp']:
            try:
                player_updates[vp[0]] = vp
            except (TypeError, IndexError):
                pass

        for i in self.players:
            if i != self.char.playerid:
                p = self.players[i]
                try:
                    p.visible = True
                    p.update(player_updates[i])
                except KeyError:
                    p.visible = False
