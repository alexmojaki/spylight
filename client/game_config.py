# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from client import utils
from client.config import config
from client.character import teams


class GameConfigScreen(Screen):
    def __init__(self, app=None, **kwargs):
        global config
        self.team = [x['name'] for x in teams]
        Builder.load_file(utils.kvPath.format('game_config_screen'))
        super(GameConfigScreen, self).__init__(**kwargs)

        team = config.get('GameConfig', 'team')
        self.cb0.active = (team == 0)
        self.cb1.active = (team == 1)
        self.serverIp.text = config.get('GameConfig', 'serverIp')

        # @TODO: GUI field
        self.serverPort = 9999
        self.gameduration = 3

        self.app = app

    def validateParameters(self):
        if self.cb0.active:
            team = 0
        else:
            team = 1

        self.app.displayGameScreen(team=team,
                                   nick=self.nick.text,
                                   serverip=self.serverIp.text,
                                   serverport=self.serverPort)
