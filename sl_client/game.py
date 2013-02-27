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

import network_protocol as np
import constants as c

from client import ClientNetworker
from slmap import SLMap
from character import Spy,Mercenary
from hud import SpylightHUD
from environment import Shadow, MapView


# server = None

# clientNetworker = None



class GameScreen(Screen):
    def __init__(self, character, mapname, serverip, gameduration, **kwargs):
        Builder.load_file('kv/game_screen.kv')
        super(GameScreen, self).__init__(**kwargs) # init with the name

        game = SpylightGame(character, mapname, serverip, gameduration)
        self.add_widget(game)

        game.start()


class SpylightGame(Widget):
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def __init__(self, character, mapname, serverip, gameduration):
        super(SpylightGame, self).__init__()

        cellMap = SLMap(mapname)
        Logger.info("SL|SLGame: Map loaded: %s", cellMap.title)
        Logger.info("SL|SLGame: Map size: (%d, %d)",
                    cellMap.width, cellMap.height) 

        srv = None # @TODO: connection stuff with serverip

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
            clientNetworker.connect(srv, 9999)

        self.soundBeep = SoundLoader.load(c.wavPath.format("beep"))
        self.soundShot = SoundLoader.load(c.wavPath.format("shot"))
        self.soundReload = SoundLoader.load(c.wavPath.format("reload"))
        self.soundModem = SoundLoader.load(c.wavPath.format("modem"))
        self.soundPunch = SoundLoader.load(c.wavPath.format("punch"))
        self.soundBoom = SoundLoader.load(c.wavPath.format("boom"))

        self.add_widget(MapView(cellMap=cellMap, character=self.character,
                                shadow=self.shadow))
        self.add_widget(self.character)

        self.started = False # What's the point of this flag?
        
        self.hud = SpylightHUD(self, gameduration)
        self.add_widget(self.hud)


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
