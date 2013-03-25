# -*- coding: utf-8 -*-

import sys

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
# from client.character import Spy, Mercenary
from client.hud import SpylightHUD
from client.environment import MapView
from client.input import KeyboardManager, TouchManager
from client.action import ActionManager
from client import utils


class GameScreen(Screen):
    def __init__(self, character, mapname, serverip, serverport, gameduration, **kwargs):
        Builder.load_file(utils.kvPath.format('game_screen'))
        super(GameScreen, self).__init__(**kwargs)  # init with the name

        # Declared here to be able to handle screen changes
        self.km = KeyboardManager()
        self.km.bind(quit=self.goToPauseScreen)
        self.tm = TouchManager()

        game = SpylightGame(character, mapname, serverip, serverport,
                            gameduration, self.km, self.tm)
        self.add_widget(game)

    def goToPauseScreen(self, instance, value):
        if not value:  # False means key up event
            Logger.info('SL|GameScreen: TODO: Pause Screen')


class SpylightGame(Widget):
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    # Simulated character
    charx = NumericProperty(Window.size[0]/2)
    chary = NumericProperty(Window.size[1]/2)
    charpos = ReferenceListProperty(charx, chary)

    def __init__(self, character, mapname, serverip, serverport, gameduration,
                 keyboardMgr, touchMgr):
        super(SpylightGame, self).__init__()

        # Register to the server
        self._ni = NetworkInterface(serverip, serverport)

        # Parse server init message
        # initString = self._ni.recieve()
        # gameduration = ?  # or remaining time
        # mapname = ?

        # Init environment
        self.map = SpyLightMap()
        self.map.load_map('test.hfm')
        Logger.info("SL|SLGame: Map loaded: %s", self.map.title)
        Logger.info("SL|SLGame: Map size: %s", self.map.size)

        self.mv = MapView(self.map)
        self.add_widget(self.mv)
        # Init char replicas

        self.hud = SpylightHUD(self, 300)
        self.add_widget(self.hud)

        # Register input listeners
        self.am = ActionManager(self._ni, keyboardMgr, touchMgr)
        keyboardMgr.bind(movement=self.move_char)  # @TODO tmp

        # Makes the map follow the character
        self.bind(charpos=self.mv.update_pos)

        # Send a message to say it's ready?

        # Game client ready
        self._ni.on_message_recieved = self.update

    def move_char(self, mgr, data):
        if data[0]:
            self.chary = self.chary - 10
        if data[1]:
            self.charx = self.charx + 10
        if data[2]:
            self.chary = self.chary + 10
        if data[3]:
            self.charx = self.charx - 10
        print self.charpos

    def update(self, timeDelta):
        Logger.info('SL|SLGame: update parameter: %s', timeDelta)
        # Prints the internal fps and the number of frames rendered
        # (if no change, it won't be rendered)
        Logger.debug('SL|SLGame: fps: %d, rfps: %d',
                     Clock.get_fps(), Clock.get_rfps())

        # self.character.update()
        # self.hud.update()
        # self.map.update()

    def end(self):
        self.playShot()
        print "The defenders won!"
        sys.exit()

    def start(self):
        self.started = True
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # self.hud.start()
