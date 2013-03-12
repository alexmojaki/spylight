# -*- coding: utf-8 -*-

import sys

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.clock import Clock

# Colored logs. the text before the first ':' will be used as log tag
from kivy.logger import Logger


import common.network_protocol as np
# import common.game_constants as c

from client.network import ClientNetworker
from common.slmap import SLMap
from client.character import Spy, Mercenary
from client.hud import SpylightHUD
from client.environment import Shadow, MapView
from client.keyboard import KeyboardManager
from client import utils


class GameScreen(Screen):
    def __init__(self, character, mapname, serverip, serverport, gameduration, **kwargs):
        Builder.load_file(utils.kvPath.format('game_screen'))
        super(GameScreen, self).__init__(**kwargs)  # init with the name

        self.km = KeyboardManager()
        self.km.bind(quit=self.goToPauseScreen)

        game = SpylightGame(character, mapname, serverip, serverport, gameduration, self.km)
        self.add_widget(game)

        game.start()

    def goToPauseScreen(self, instance, value):
        if not value:  # False means key up event
            Logger.info('SL|GameScreen: TODO: Pause Screen')


class SpylightGame(Widget):
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def __init__(self, character, mapname, serverip, serverport, gameduration, keyboardMgr):
        super(SpylightGame, self).__init__()

        cellMap = SLMap(mapname)
        Logger.info("SL|SLGame: Map loaded: %s", cellMap.title)
        Logger.info("SL|SLGame: Map size: (%d, %d)",
                    cellMap.width, cellMap.height)

        srv = serverip
        if serverip == "Debug":  # @TODO remove these 2 lines once the server is stable.
            srv = None

        if character == Mercenary.name:
            self.character = Mercenary(game=self, cellMap=cellMap, server=srv)
            self.shadow = Shadow(Spy.sprite)
            if srv:
                clientNetworker = ClientNetworker(np.MERCENARY_TYPE)
        else:
            self.character = Spy(game=self, cellMap=cellMap, server=srv)
            self.shadow = Shadow(Mercenary.sprite)
            if srv:
                clientNetworker = ClientNetworker(np.SPY_TYPE)

        if srv:
            clientNetworker.connect(srv, serverport)

        self.soundBeep = SoundLoader.load(utils.wavPath.format("beep"))
        self.soundShot = SoundLoader.load(utils.wavPath.format("shot"))
        self.soundReload = SoundLoader.load(utils.wavPath.format("reload"))
        self.soundModem = SoundLoader.load(utils.wavPath.format("modem"))
        self.soundPunch = SoundLoader.load(utils.wavPath.format("punch"))
        self.soundBoom = SoundLoader.load(utils.wavPath.format("boom"))

        self.add_widget(MapView(cellMap=cellMap, character=self.character,
                                shadow=self.shadow))
        self.add_widget(self.character)

        self.started = False  # What's the point of this flag?

        self.hud = SpylightHUD(self, gameduration)
        self.add_widget(self.hud)

        keyboardMgr.bind(up=self.character.upEvt)
        keyboardMgr.bind(left=self.character.leftEvt)
        keyboardMgr.bind(down=self.character.downEvt)
        keyboardMgr.bind(right=self.character.rightEvt)
        keyboardMgr.bind(run=self.character.runEvt)
        keyboardMgr.bind(action=self.character.actionEvt)

    def update(self, timeDelta):
        # Prints the internal fps and the number of frames rendered
        # (if no change, it won't be rendered)
        Logger.debug('SL|SLGame: fps: %d, rfps: %d',
                     Clock.get_fps(), Clock.get_rfps())

        self.character.update()
        self.hud.update()

    def end(self):
        self.playShot()
        print "The defenders won!"
        sys.exit()

    def start(self):
        self.started = True
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.hud.start()

    def playBeep(self):
        self.soundBeep.play()

    def playShot(self):
        self.soundShot.play()

    def playReload(self):
        self.soundReaload.play()

    def playModem(self):
        self.soundModem.play()

    def stopModem(self):
        self.soundModem.stop()

    def playPunch(self):
        self.soundPunch.play()

    def playBoom(self):
        self.soundBoom.play()
