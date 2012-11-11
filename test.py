from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.graphics import Mesh
from kivy.clock import Clock
from kivy.factory import Factory


class MyGrid(Widget):
    x1 = NumericProperty(150)
    y1 = NumericProperty(100)
    u1 = NumericProperty(0)
    v1 = NumericProperty(0)
    i1 = NumericProperty(0)
    x2 = NumericProperty(100)
    y2 = NumericProperty(200)
    u2 = NumericProperty(0)
    v2 = NumericProperty(0)
    i2 = NumericProperty(1)
    x3 = NumericProperty(200)
    y3 = NumericProperty(200)
    u3 = NumericProperty(0)
    v3 = NumericProperty(0)
    i3 = NumericProperty(2)
    x4 = NumericProperty(300)
    y4 = NumericProperty(300)
    u4 = NumericProperty(0)
    v4 = NumericProperty(0)
    i4 = NumericProperty(3)
    vertices = ReferenceListProperty(x1, y1, u1, v1, x2, y2, u2, v2, x3, y3, u3, v3, x4, y4, u4, v4)
    indices = ReferenceListProperty(i1, i2, i3, i4)

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

Factory.register("Mesh", Mesh)

class MyApp(App):
    def build(self):
        mg = MyGrid()
        Clock.schedule_interval(mg.update, 1.0 / 60.0)
        return mg

if __name__ == '__main__':
    MyApp().run()
