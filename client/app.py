#!/usr/bin/python

import kivy
kivy.require('1.5.1')

from client.utils import spritePath
# Changing kivy specific settings: must be done before loading other stuff.
from kivy.config import Config #http://kivy.org/docs/api-kivy.config.html
Config.set('kivy', 'window_icon', spritePath.format('mercenary')) 
Config.set('kivy', 'log_level', 'info')  # Change here to see debug messages
# Config.set('kivy', 'log_enable', '0') 
# Config.set('graphics', 'width', '400') 
# Config.set('graphics', 'height', '400') 
# Config.set('graphics', 'fullscreen', 'auto') # Warning: sucks

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from client.menu import MenuScreen
from client.game import GameScreen
from client.game_config import GameConfigScreen


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
        return self.sm

    def displayGameConfigScreen(self):
        self.sm.current = "GameConfig"
    
    def displayGameScreen(self, **kwargs):
        game = GameScreen(app=self, name="Game", **kwargs)
        self.sm.add_widget(game)
        self.sm.current = "Game"
    
    def displayMenuScreen(self):
        self.sm.current = "Menu"


if __name__ == '__main__':
    # Changing kivy specific settings
    SpylightClientApp().run()