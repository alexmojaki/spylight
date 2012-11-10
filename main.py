#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join
from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock

import logging

from slmap import SLMap

class SpylightGame(Widget):

    def __init__(self, **kwargs):
        super(SpylightGame, self).__init__(**kwargs)
        # self.add_widget(MapView(self.size))

class MapView(Widget):
    def getTexture(self,name, size):
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        self.logger.info(filename)
        return texture

    def __init__(self, map):
        super(MapView, self).__init__()
        self.logger = logging.getLogger("SpylightApp")
        tileSize = 32
        ground = self.getTexture(name='ground', size=(32,32))
        wall = self.getTexture(name='wall', size=(32,32))

        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=(0,0), size=(map.width*tileSize, map.height*tileSize), texture=ground)

        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    wall = Wall()
                    wall.pos = (x*tileSize, y*tileSize)
                    self.add_widget(wall)
                    

class Wall(Widget):
    pass



class SpylightApp(App):
    def initLogger(self):
        self.logger = logging.getLogger("SpylightApp")
        self.logger.addHandler(logging.FileHandler("spylight.log"))
        self.logger.setLevel(logging.INFO)

    def build(self):
        self.initLogger()

        map = SLMap("test.map")
        self.logger.info("Map loaded: " + map.title)
        self.logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")

        self.logger.info("What in (1, 1): " + str(map.getWallType(1, 1)))
        spy = Spy()
        game = SpylightGame()
        game.add_widget(MapView(map=map))
        game.add_widget(spy)

        Clock.schedule_interval(spy.update, 1.0/60.0)
        return game

class Spy(Widget):
    # velocity_x = NumericProperty(0)
    # velocity_y = NumericProperty(0)
    # velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super(Spy, self).__init__(**kwargs)

        self.zPressed = False
        self.qPressed = False
        self.sPressed = False
        self.dPressed = False

        self.pos = Vector(0,0)

        self.velocity = Vector(0,0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        # with self.canvas:
        #     Color(0.5,0.5,0.5)
        #     Rectangle(size=(10,10), pos=self.pos)

    def _keyboard_closed(self):
        print 'My keyboard have been closed!'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print 'The key', keycode, 'have been pressed'
        # print ' - text is %r' % text
        # print ' - modifiers are %r' % modifiers
        
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

    def _on_keyboard_up(self, truc, keycode):

        if keycode[1] == 'z':
            self.zPressed = False
        if keycode[1] == 'q':
            self.qPressed = False
        if keycode[1] == 's':
            self.sPressed = False
        if keycode[1] == 'd':
            self.dPressed = False

        return True

    def update(self, truc, **kwargs):

        maxVelocity = 4
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

        self.pos = self.velocity + self.pos

        # print 'pos ' + str(self.pos)

        for i in xrange(0,2):
            if self.velocity[i] < 0:
                self.velocity[i] += deceleration
            elif self.velocity[i] > 0:
                self.velocity[i] -= deceleration


if __name__ == '__main__':
    SpylightApp().run()

