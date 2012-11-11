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
import logging
import math

import network_protocol as np
from client import ClientNetworker
from slmap import SLMap

map = None
character = None
server = None
logger = None
CELL_SIZE = 32
clientNetworker = None
game = None
shadow = None

class SpylightGame(Widget):
    character = ObjectProperty(None)

    def __init__(self, character, map, **kwargs):
        global shadow
        super(SpylightGame, self).__init__(**kwargs)

        self.soundBeep = SoundLoader.load("music/beep.wav")
        self.soundShot = SoundLoader.load("music/shot.wav")
        self.soundReload = SoundLoader.load("music/reload.wav")

        shadow = Shadow()
        self.character = character
        self.add_widget(MapView(map=map, character=self.character))
        self.add_widget(character)

    def update(self, useless, **kwargs):
        self.character.update(kwargs)

    def playBeep(self):
        self.soundBeep.play()

    def playShot(self):
        self.soundShot.play()

    def playReload(self):
        self.soundReaload.play()

class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)

    def getTexture(self,name, size):
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        self.logger.info(filename)
        return texture

    def __init__(self, map, character):
        self.character = character

        super(MapView, self).__init__()
        self.logger = logging.getLogger("SpylightApp")
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



class Character(Widget):
    x1 = NumericProperty(0)
    y1 = NumericProperty(0)
    x2 = NumericProperty(0)
    y2 = NumericProperty(100)
    x3 = NumericProperty(100)
    y3 = NumericProperty(100)
    points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)

        self.zPressed = False
        self.qPressed = False
        self.sPressed = False
        self.dPressed = False
        self.ePressed = False
        self.velocity = Vector(0,0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        # print 'My keyboard have been closed!'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        pos2 = self.pos
        # Keycode is composed of an integer + a string
        if keycode[1] == 'z':
            self.zPressed = True
        if keycode[1] == 'q':
            self.qPressed = True
        if keycode[1] == 's':
            self.sPressed = True
        if keycode[1] == 'd':
            self.dPressed = True

        return True

    def _on_keyboard_up(self, useless, keycode):

        if keycode[1] == 'z':
            self.zPressed = False
        if keycode[1] == 'q':
            self.qPressed = False
        if keycode[1] == 's':
            self.sPressed = False
        if keycode[1] == 'd':
            self.dPressed = False
        if keycode[1] == 'e':
            self.activate()

        return True

    def activate(self):
        pass


    def update(self, useless, **kwargs):

        maxVelocity = 3
        deceleration = 1
        # print 'update', self.velocity

        if self.zPressed:
            if self.sPressed:
                self.velocity[1] = 0
            else:
                self.velocity[1] = maxVelocity
        else:
             if self.sPressed:
                self.velocity[1] = -maxVelocity

        if self.qPressed:
            if self.dPressed:
                self.velocity[0] = 0
            else:
                self.velocity[0] = -maxVelocity
        else:
            if self.dPressed:
                self.velocity[0] = maxVelocity

        # print 'velocity ' + str(self.velocity)

        pos2 = self.velocity + self.pos
        if(self.canGo(pos2)):
            self.pos = pos2


        for i in xrange(0,2):
            if self.velocity[i] < 0:
                self.velocity[i] += deceleration
            elif self.velocity[i] > 0:
                self.velocity[i] -= deceleration

        heading = (Vector(*Window.mouse_pos) - Vector(self.center_x, self.center_y)).angle(Vector(0, 1))
        self.x1, self.y1 = self.center_x, self.center_y
        self.x2, self.y2 = Vector(-50, 100).rotate(heading) + [self.center_x, self.center_y]
        self.x3, self.y3 = Vector(50, 100).rotate(heading) + [self.center_x, self.center_y]

        if server:
            self.notifyServer()

        # print 'Position',self.pos, 'Triangle', self.points

    def canGo(self,pos2):
        margin = 7
        ret = map.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        logger.debug(pos2, (pos2[0]+margin)/CELL_SIZE,(pos2[1]+margin)/CELL_SIZE)

        return ret

    def notifyServer(self):
        clientNetworker.pos(*self.pos)
        clientNetworker.mouse_pos(*Window.mouse_pos)
        clientNetworker.send()

        self.displayReception()
    
    def displayReception(self):
        global game
        ret = clientNetworker.recv()

        shadow.pos = ret.pos

        if ret.beep:
            game.playBeep()

        if ret.gameOver:
            pass




class Spy(Character):
    def __init__(self, **kwargs):
        logger.info('init spy')
        self.sprite = 'art/spy.png'
        self.pos = (CELL_SIZE,CELL_SIZE)
        super(Spy, self).__init__(**kwargs)

    def update(self, useless, **kwargs):
        super(Spy,self).update(useless, **kwargs)
        logger.info('Spy is updating!')

    def activate(self):
        super(Spy,self).activate()
        clientNetworker.activate()
        logger.info('Spy is activating!')


class Mercenary(Character):
    def __init__(self, **kwargs):
        global map
        logger.info('init mercenary')
        self.sprite = 'art/mercenary.png'
        self.pos = (map.spawnPoints[map.Mercenary])
        super(Mercenary, self).__init__(**kwargs)

    def update(self, useless, **kwargs):
        super(Mercenary,self).update(useless, **kwargs)
        logger.info('Mercenary is updating!')

    def activate(self):
        super(Mercenary,self).activate()
        clientNetworker.drop(np.OT_MINE)
        # Mine()
        logger.info('Mercenary is activating!')


class Wall(Widget):
    pass


class Terminal(Widget):
    pass

class Shadow(Widget):
    pass

class Mine(Widget):
    pass


Factory.register("MapView", MapView)


class SpylightApp(App):

    def initLogger(self):
        logger = logging.getLogger("SpylightApp")
        logger.addHandler(logging.FileHandler("spylight.log"))
        logger.setLevel(logging.INFO)
        return logger

    def build(self):
        global map, logger, clientNetworker, game
        logger = self.initLogger()

        if server:
            clientNetworker = ClientNetworker(np.SPY_TYPE)
            clientNetworker.connect(server, 9999)

        map = SLMap("test.map")
        logger.info("Map loaded: " + map.title)
        logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")

        logger.info("What in (4, 8): " + str(map.getItem(4, 8)))

        if character == 'merc':
            pass
            char = Mercenary()
        else:
            char = Spy()



        game = SpylightGame(character=char, map=map)

        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game

if __name__ == '__main__':
    global character, server
    if len(sys.argv) >= 2:
        character = sys.argv[1]

    if len(sys.argv) >= 3:
        server = sys.argv[2]

    SpylightApp().run()
