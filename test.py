from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget

class MyGrid(Widget):
    def __init__(self):
        super(MyGrid,self).__init__()
        texture = Image('art/wall.png').texture
        texture.wrap = 'repeat'
        texture.uvsize = (32, 32)
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=(0, 0), size=(2000, 2000), texture=texture)

class MyApp(App):
    def build(self):
        return MyGrid()

if __name__ == '__main__':
    MyApp().run()