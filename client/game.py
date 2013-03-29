# -*- coding: utf-8 -*-

import sys
from ast import literal_eval

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.clock import Clock

# Colored logs. the text before the first ':' will be used as log tag
from kivy.logger import Logger


# import common.network_protocol as np
# import common.game_constants as c

from client.network import NetworkInterface
# from common.slmap import SLMap
from common.map_parser import SpyLightMap
from client.character import Character
from client.hud import SpylightHUD
from client.environment import MapView
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
        init_response = self._ni.connect({'team': team, 'nick': nick})

        # Parse server init message
        self.team = init_response['team']
        self.nick = nick
        self.playerid = init_response['id']
        self.players = init_response['players']

        # Init environment
        loaded_map = SpyLightMap(init_response['map'])
        Logger.info("SL|SLGame: Map loaded: %s", loaded_map.title)
        Logger.info("SL|SLGame: Map size: %s", loaded_map.size)

        if init_response['map_hash'] != loaded_map.get_hash():
            Logger.error("SL|SLGame: Wrong map hash")
            sys.exit()

        self.mv = MapView(loaded_map)
        self.add_widget(self.mv)
        # Init char replicas

        self.char = Character(self.team, init_response['pos'],
                              self.mv.update_pos)
        self.add_widget(self.char)

        self.hud = SpylightHUD(self, 300)
        self.add_widget(self.hud)

        # Register input listeners
        self.am = ActionManager(self._ni, keyboardMgr, touchMgr)

        # Send a message to say it's ready?

        # Game client ready
        self._ni.on_message_recieved = self.update
        print "ready"

    def update(self, data):
        Logger.debug('SL|SLGame: update parameter: %s', data)
        # Prints the internal fps and the number of frames rendered
        # (if no change, it won't be rendered)
        Logger.debug('SL|SLGame: fps: %d, rfps: %d',
                     Clock.get_fps(), Clock.get_rfps())

        data = literal_eval(data)
        new_pos = data['p']
        self.char.set_game_pos(new_pos)
        # To update:
        #   view cone
        #   hud
        #   map elements

    def end(self):
        self.playShot()
        print "The defenders won!"
        sys.exit()

    def start(self):
        self.started = True
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # self.hud.start()
