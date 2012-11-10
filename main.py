#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join
from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory

import logging

from slmap import SLMap

map = None

class SpylightGame(Widget):

    def __init__(self, **kwargs):
        super(SpylightGame, self).__init__(**kwargs)

class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    spy = ObjectProperty(None)

    def getTexture(self,name, size):
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        self.logger.info(filename)
        return texture

    def __init__(self, map, spy):
        self.spy = spy
        super(MapView, self).__init__()
        tileSize = 32
        self.logger = logging.getLogger("SpylightApp")
        self.width = map.width*tileSize
        self.height = map.height*tileSize
        self.groundTexture = self.getTexture(name='ground', size=(32,32))
        # ground = self.getTexture(name='ground', size=(32,32))
        # wall = self.getTexture(name='wall', size=(32,32))
        
        print spy.points

        # with self.canvas:    
            # StencilPush()
            # Triangle(points=spy.points)
            # StencilUse()
            # Rectangle(pos=(0,0), size=(self.width, self.height), texture=self.groundTexture)
            # StencilUnUse()
            # # Triangle(points=spy.points)
            # StencilPop()
            
        # with self.canvas:
        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    wall = Wall()
                    wall.pos = (x*tileSize, y*tileSize)
                    self.add_widget(wall)            

class Wall(Widget):
    pass




class Spy(Widget):
    x1 = NumericProperty(0)
    y1 = NumericProperty(0)
    x2 = NumericProperty(0)
    y2 = NumericProperty(100)
    x3 = NumericProperty(100)
    y3 = NumericProperty(100)
    points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)

    def __init__(self, **kwargs):
        super(Spy, self).__init__(**kwargs)

        self.zPressed = False
        self.qPressed = False
        self.sPressed = False
        self.dPressed = False

        self.velocity = Vector(0,0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        print 'My keyboard have been closed!'
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

        return True

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



        self.x1, self.y1 = self.center_x, self.center_y
        self.x2, self.y2 = self.x1 - 50, self.y1 + 100
        self.x3, self.y3 = self.x1 + 50, self.y1 + 100

        print 'Position',self.pos, 'Triangle', self.points

    def canGo(self,pos2):
        margin = 7
        ret = map.getWallType((pos2[0]+margin)/32, (pos2[1]+margin)/32) == -1
        ret = ret and map.getWallType((pos2[0]+32-margin)/32, (pos2[1]+32-margin)/32) == -1
        ret = ret and map.getWallType((pos2[0]+margin)/32, (pos2[1]+32-margin)/32) == -1
        ret = ret and map.getWallType((pos2[0]+32-margin)/32, (pos2[1]+margin)/32) == -1
        print pos2, (pos2[0]+margin)/32,(pos2[1]+margin)/32

        return ret


Factory.register("MapView", MapView)

class SpylightApp(App):
    def initLogger(self):
        self.logger = logging.getLogger("SpylightApp")
        self.logger.addHandler(logging.FileHandler("spylight.log"))
        self.logger.setLevel(logging.INFO)

    def build(self):
        global map
        self.initLogger()

        map = SLMap("test.map")
        self.logger.info("Map loaded: " + map.title)
        self.logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")

        self.logger.info("What in (1, 1): " + str(map.getWallType(1, 1)))
        spy = Spy()

        game = SpylightGame()
        game.add_widget(MapView(map=map, spy=spy))
        game.add_widget(spy)

        Clock.schedule_interval(spy.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    SpylightApp().run()

