#!/usr/bin/python
# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.widget import Widget

from slmap import SLMap

class SpylightGame(Widget):
    pass

class SpylightApp(App):
    def build(self):
        print SLMap("test.map").title
        return SpylightGame()

if __name__ == '__main__':
    SpylightApp().run()
