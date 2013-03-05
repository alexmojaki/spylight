#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join
from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory
import sys
# import logging
import math

import network_protocol as np
from client import ClientNetworker
from slmap import SLMap
from character import Spy,Mercenary
import custom_logger as c

from kivy.config import Config


map = None
character = None
server = None
logger = None
CELL_SIZE = 32
MAX_MIN_COUNTDOWN = 3
clientNetworker = None
game = None
capInfo = None

class SpylightGame(Widget):
    character = ObjectProperty(None)

    def __init__(self, character, cellMap, **kwargs):
        super(SpylightGame, self).__init__(**kwargs)

        if character == 'merc':
            self.character = Mercenary(game=self, cellMap=cellMap, server=server)
            shadow = Shadow('art/spy.png')
            if server:
                clientNetworker = ClientNetworker(np.MERCENARY_TYPE)
        else:
            self.character = Spy(game=self, cellMap=cellMap, server=server)
            shadow = Shadow('art/mercenary.png')
            if server:
                clientNetworker = ClientNetworker(np.SPY_TYPE)

        if server:
            clientNetworker.connect(server, 9999)

        self.soundBeep = SoundLoader.load("music/beep.wav")
        self.soundShot = SoundLoader.load("music/shot.wav")
        self.soundReload = SoundLoader.load("music/reload.wav")
        self.soundModem = SoundLoader.load("music/modem.wav")
        self.soundPunch = SoundLoader.load("music/punch.wav")
        self.soundBoom = SoundLoader.load("music/boom.wav")

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
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        self.logger.info(filename)
        return texture

    def __init__(self, map, character, shadow):
        self.character = character
        self.shadow = shadow

        super(MapView, self).__init__()
        self.logger = c.logger
        self.width = map.width*CELL_SIZE
        self.height = map.height*CELL_SIZE
        self.groundTexture = self.getTexture(name='wall2', size=(CELL_SIZE,CELL_SIZE))

        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    wall = Wall()
                    wall.pos = (x*CELL_SIZE, y*CELL_SIZE)
                    self.add_widget(wall)
                if map.getItem(x,y) == 0:
                    term = Terminal()
                    term.pos = (x*CELL_SIZE, y*CELL_SIZE)
                    self.add_widget(term)


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
#         c.logger.info("cap info created")
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

Factory.register("MapView", MapView)
Factory.register("Shadow", Shadow)


class SpylightApp(App):

    def build(self):
        global map, clientNetworker, game


        map = SLMap("test.map")
        c.logger.info("Map loaded: " + map.title)
        c.logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")        

        game = SpylightGame(self.character, map)

        Clock.schedule_interval(game.update, 1.0 / 60.0)

        game.start()

        return game

if __name__ == '__main__':
    global character, server
    
    if len(sys.argv) >= 2:
        character = sys.argv[1]

    if len(sys.argv) >= 3:
        server = sys.argv[2]

    app = SpylightApp()
    app.character = character
    app.server = server

    app.run()
