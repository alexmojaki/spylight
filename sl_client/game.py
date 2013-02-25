#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Triangle,Color, Rectangle, StencilPush, StencilUse, StencilPop, StencilUnUse
# from kivy.uix.button import Button
from kivy.uix.widget import Widget
# from kivy.core.window import Window
from kivy.core.audio import SoundLoader
# from kivy.vector import Vector
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.stencilview import StencilView
import sys
# import logging
# import math

import network_protocol as np
from client import ClientNetworker
from slmap import SLMap
from character import Spy,Mercenary
from custom_logger import logger

# from kivy.config import Config


map = None
character = None
server = None
CELL_SIZE = 32
MAX_MIN_COUNTDOWN = 3
clientNetworker = None
game = None
capInfo = None
artDir = 'art'
musicDir = '../music'
texturePath = 'art/{0}.png'
wavPath = 'art/{0}.wav'

class GameScreen(Screen):
    def __init__(self, app, character, serverip, mapname, **kwargs):
        global map, clientNetworker, game

        Builder.load_file('kv/game_screen.kv')
        super(Screen, self).__init__(**kwargs)

        self.app = app

        map = SLMap(mapname)
        logger.info("Map loaded: " + map.title)
        logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")        
        game = SpylightGame(character, map)
        self.add_widget(game)

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        game.start()
        # return game        



class SpylightGame(Widget):
    character = ObjectProperty(None)

    def __init__(self, character, cellMap, **kwargs):
        Builder.load_file('kv/spylight.kv')
        super(SpylightGame, self).__init__(**kwargs)

        if character == 'merc':
            self.character = Mercenary(game=self, cellMap=cellMap, server=server)
            shadow = Shadow(texturePath.format('spy'))
            if server:
                clientNetworker = ClientNetworker(np.MERCENARY_TYPE)
        else:
            self.character = Spy(game=self, cellMap=cellMap, server=server)
            shadow = Shadow(texturePath.format('mercenary'))
            if server:
                clientNetworker = ClientNetworker(np.SPY_TYPE)

        if server:
            clientNetworker.connect(server, 9999)

        self.soundBeep = SoundLoader.load(wavPath.format("beep"))
        self.soundShot = SoundLoader.load(wavPath.format("shot"))
        self.soundReload = SoundLoader.load(wavPath.format("reload"))
        self.soundModem = SoundLoader.load(wavPath.format("modem"))
        self.soundPunch = SoundLoader.load(wavPath.format("punch"))
        self.soundBoom = SoundLoader.load(wavPath.format("boom"))

        self.add_widget(MapView(map=map, character=self.character, shadow=shadow))
        self.add_widget(self.character)
        # self.capInfo = CapInfo()
        # self.add_widget(capInfo)
        self.started = False

    def update(self, useless, **kwargs):
        self.character.update(kwargs)
        # self.capInfo.update(kwargs)

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

    def end(self):
        game.playShot()
        print "The mercenary won!"
        sys.exit()

    def start(self):
        timer = Timer()
        game.add_widget(timer)
        Clock.schedule_interval(timer.updateTime, 1)
        self.started = True



class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def getTexture(self,name, size):
        filename = texturePath.format(name)
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        logger.info(filename)
        return texture

    def __init__(self, map, character, shadow):
        self.character = character
        self.shadow = shadow

        super(MapView, self).__init__(size=(map.width*CELL_SIZE,map.height*CELL_SIZE))
        self.groundTexture = self.getTexture(name='wall2', size=(CELL_SIZE,CELL_SIZE))

        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    self.add_widget(Wall(pos=(x*CELL_SIZE, y*CELL_SIZE)))
                if map.getItem(x,y) == 0:
                    self.add_widget(Terminal(pos=(x*CELL_SIZE, y*CELL_SIZE)))


class Wall(Widget):
    pass


class Terminal(Widget):
    pass


class Shadow(Widget):
    def __init__(self, sprite, **kwargs):
        self.sprite = sprite
        super(Shadow, self).__init__(**kwargs)


class Mine(Widget):
    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10;
        super(Mine, self).__init__(**kwargs)

# class CapInfo(Widget):
#     percentage = StringProperty("0%")

#     def __init__(self, **kwargs):
#         logger.info("cap info created")
#         super(CapInfo, self).__init__(**kwargs)

#     def update(self, newValue):
#         self.percentage = str(newValue)+'%'



class Timer(Widget):
    time = StringProperty("00:00")


    def __init__(self, **kwargs):
        self.mins = MAX_MIN_COUNTDOWN
        self.secs = 0
        self.timeToString()
        super(Timer, self).__init__(**kwargs)

    def timeToString(self):
        self.time = '0'+str(self.mins)+':'
        if self.secs < 10:
            self.time += '0' + str(self.secs)
        else:
            self.time += str(self.secs)


    def updateTime(self, useless):
        global game
        self.secs -= 1
        if self.secs == -1:
            self.mins -= 1
            self.secs = 59

        self.timeToString()
        if self.mins == 0 and self.secs == 0:
            game.end()

# Factory.register("MapView", MapView)
# Factory.register("Shadow", Shadow)
