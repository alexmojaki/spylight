from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# from main import app

class GameScreen(Screen):
    def __init__(self, app=None, **kwargs):
        Builder.load_file('kv/game_screen.kv')
        super(Screen, self).__init__(**kwargs)

        self.app = app