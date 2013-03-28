# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from client import utils
from client.config import config


class GameConfigScreen(Screen):
    def __init__(self, app=None, **kwargs):
        global config
        Builder.load_file(utils.kvPath.format('game_config_screen'))
        super(GameConfigScreen, self).__init__(**kwargs)

        role = config.get('GameConfig', 'character')
        self.cbSpy.active = (role == 'spy')
        self.cbMerc.active = (role == 'merc')
        self.map.text = "TODO système chargement map serveur"
        self.serverIp.text = config.get('GameConfig', 'serverIp')

        # @TODO: GUI field
        self.serverPort = 9999
        self.gameduration = 3

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
        self.app.displayGameScreen(character=role,
                                   mapname='test2.map',
                                   serverip=self.serverIp.text,
                                   serverport=self.serverPort,
                                   gameduration=self.gameduration)
