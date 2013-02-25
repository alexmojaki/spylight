#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# from main import app

class GameConfigScreen(Screen):
    def __init__(self, app=None, **kwargs):
        Builder.load_file('kv/game_config_screen.kv')
        super(Screen, self).__init__(**kwargs)

        role = kwargs.get('character')
        self.cbSpy.active = (role == 'spy')
        self.cbMerc.active = (role == 'merc')
        self.map.text = "TODO système chargement map serveur"
        self.serverIp.text = kwargs.get('serverIp', '127.0.0.1')
        self.app = app

    def validateParameters(self):
        print self.cbSpy.active
        print self.cbMerc.active
        print self.serverIp.text

        # TODO: Check if the other player is ready, params are good, etc
        if self.cbSpy.active:
            role = 'spy'
        else:
            role = 'merc'
        self.app.displayGameScreen(role, '../test.map', self.serverIp.text)