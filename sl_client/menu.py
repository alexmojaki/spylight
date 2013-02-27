from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class MenuScreen(Screen):
    def __init__(self, app=None, **kwargs):
        Builder.load_file('kv/menu_screen.kv')
        super(MenuScreen, self).__init__(**kwargs)

        self.app = app
    
    def play(self):
        self.app.displayGameConfigScreen()

    def stopApp(self):
        self.app.stop()