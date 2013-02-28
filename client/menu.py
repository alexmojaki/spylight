from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from client.utils import kvPath

class MenuScreen(Screen):
    def __init__(self, app=None, **kwargs):
        Builder.load_file(kvPath.format('menu_screen'))
        super(MenuScreen, self).__init__(**kwargs)

        self.app = app
    
    def play(self):
        self.app.displayGameConfigScreen()

    def stopApp(self):
        self.app.stop()