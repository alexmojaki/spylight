import kivy
from kivy.app import App
from kivy.uix.widget import Widget

class SpylightGame(Widget):
    pass

class SpylightApp(App):
    def build(self):
        return SpylightGame()

if __name__ == '__main__':
    SpylightApp().run()
