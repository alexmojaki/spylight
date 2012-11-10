#!/usr/bin/python
# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.widget import Widget

import logging

from slmap import SLMap

class SpylightGame(Widget):
    pass

class SpylightApp(App):
    def initLogger(self):
        self.logger = logging.getLogger("SpylightApp")
        self.logger.addHandler(logging.FileHandler("spylight.log"))
        self.logger.setLevel(logging.INFO)

    def build(self):
        self.initLogger()
        self.logger.info(SLMap("test.map").title)
        return SpylightGame()

if __name__ == '__main__':
    SpylightApp().run()
