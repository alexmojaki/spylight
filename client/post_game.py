# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from client import utils
from client.character import teams


class PostGameScreen(Screen):
    def __init__(self, app, data, **kwargs):
        Builder.load_file(utils.kvPath.format('post_game_screen'))
        self.game_duration = str(data['ttime'])
        self.win_msg = teams[data['winners']]['win_msg']
        self.app = app
        super(PostGameScreen, self).__init__(**kwargs)

    def quit(self):
        self.app.stop()
