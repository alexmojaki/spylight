from kivy.app import App
# from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image

class MyGrid(Widget):
    def __init__(self):
        super(MyGrid,self).__init__()
        # texture = Image('art/wall2.png').texture
        # texture.wrap = 'repeat'
        # texture.uvsize = (32, 32)
        with self.canvas:
            Color(1, 1, 1)
            # Rectangle(pos=(0, 0), size=(2000, 2000), texture=texture)
            # Image(pos=(0,0), size=(40,40), source='alt/ground.png')

class MyApp(App):
    def build(self):
        return MyGrid()

if __name__ == '__main__':
    MyApp().run()