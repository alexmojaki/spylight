import kivy
kivy.require('1.5.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from menu import MenuScreen
from game import GameScreen
from game_config import GameConfigScreen


## Classes ####################################################################

class SpylightClientApp(App):
    def build_config(self, config):
        config.setdefaults('GameConfig', {
            'serverIp': '127.0.0.1',
            'character': 'spy'
        })

    def build(self):
        # Transition duration can't be 0 (division by 0)
        self.sm = ScreenManager(transition=FadeTransition(duration=0.001)) 
        self.sm.add_widget(MenuScreen(app=self, name="Menu"))
        self.sm.add_widget(GameConfigScreen(app=self, name="GameConfig",
                                            character=self.config.get('GameConfig', 'character'),
                                            serverIp=self.config.get('GameConfig','serverIp')))
        self.sm.add_widget(GameScreen(app=self, name="Game"))
        return self.sm

    def displayGameConfigScreen(self):
        self.sm.current = "GameConfig"
    
    def displayGameScreen(self):
        self.sm.current = "Game"
    
    def displayMenuScreen(self):
        self.sm.current = "Menu"


if __name__ == '__main__':
    SpylightClientApp().run()