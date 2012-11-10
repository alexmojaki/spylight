#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join
from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget

import logging

from slmap import SLMap

class SpylightGame(Widget):

    def __init__(self, **kwargs, logger):
        super(SpylightGame, self).__init__(**kwargs)
        self.logger = logger
        print self.parent
        self.add_widget(MapView(self.size))

class MapView(Widget):
    def getTexture(self,name, size):
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        return texture

    def __init__(self,size):
        super(MapView, self).__init__()
        ground = self.getTexture(name='ground', size=(32,32))
        print str(size);
        # texture = Image('art/ground.png').texture
        # texture.wrap = 'repeat'
        # texture.uvsize = (32, 32)
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=(0,0), size=size, texture=ground)
            # show our fbo on the widget in different size
            # Rectangle(pos=(32, 0), size=(64, 64), texture=self.fbo.texture)
            # Rectangle(pos=(96, 0), size=(128, 128), texture=self.fbo.texture)

class SpylightApp(App):
    def initLogger(self):
        self.logger = logging.getLogger("SpylightApp")
        self.logger.addHandler(logging.FileHandler("spylight.log"))
        self.logger.setLevel(logging.INFO)

    def build(self):

        # root = Widget()

        # texture = Image('art/ground.png').texture
        # texture.wrap = 'repeat'
        # texture.uvsize = (32, 32)
        # with root.canvas:
        #     Rectangle(pos=(0,0), size=(200,200), texture=texture)

        # root.add_widget(MapView())
        # root.add_widget(SpylightGame())
        self.initLogger()

        map = SLMap("test.map")
        self.logger.info("Map loaded: " + map.title)

        self.logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")
        self.logger.info("What in (1, 1): " + str(map.getWallType(1, 1)))
        return SpylightGame(self.logger)

if __name__ == '__main__':
    SpylightApp().run()

    # ground = getTexture(name='ground', size=(32,32))
# class MyKeyboardListener(Widget):

#     def __init__(self, **kwargs):
#         super(MyKeyboardListener, self).__init__(**kwargs)
#         self._keyboard = Window.request_keyboard(
#             self._keyboard_closed, self)
#         self._keyboard.bind(on_key_down=self._on_keyboard_down)

#     def _keyboard_closed(self):
#         print 'My keyboard have been closed!'
#         self._keyboard.unbind(on_key_down=self._on_keyboard_down)
#         self._keyboard = None

#     def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#         print 'The key', keycode, 'have been pressed'
#         print ' - text is %r' % text
#         print ' - modifiers are %r' % modifiers

#         # Keycode is composed of an integer + a string
#         # If we hit escape, release the keyboard
#         if keycode[1] == 'escape':
#             keyboard.release()

#         # Return True to accept the key. Otherwise, it will be used by
#         # the system.
#         return True
