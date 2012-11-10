from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock

class MyGrid(Widget):
    x1 = NumericProperty(150)
    y1 = NumericProperty(100)
    x2 = NumericProperty(100)
    y2 = NumericProperty(200)
    x3 = NumericProperty(200)
    y3 = NumericProperty(200)
    points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)

    def update(self, dt):
        self.x1, self.y1 = Window.mouse_pos
        self.x2, self.y2 = self.x1 - 50, self.y1 + 100
        self.x3, self.y3 = self.x1 + 50, self.y1 + 100

#   def __init__(self):
#      super(MyGrid,self).__init__()
#       texture = Image('art/wall2.png').texture
#       texture.wrap = 'repeat'
#       texture.uvsize = (32, 32)
#       with self.canvas:
#           Color(1, 1, 1)
#           Rectangle(pos=(0, 0), size=(2000, 2000), texture=texture)

#   def addTorchStencil(x, y):
#       pass

class MyApp(App):
    def build(self):
        mg = MyGrid()
        Clock.schedule_interval(mg.update, 1.0 / 60.0)
        return mg

if __name__ == '__main__':
    MyApp().run()
