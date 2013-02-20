#!/usr/bin/python

# from kivy.app import App
# from kivy.graphics import Color, Rectangle, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle, Line
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, ObjectProperty, StringProperty, AliasProperty 
from kivy.graphics import Color, Rectangle, Line, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle, Ellipse
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock

# from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.app import App

# Note : It is working using the .kv
Builder.load_string('''
<TestStencil>:
    canvas:
        StencilPush
        Rectangle:
            pos: 300, 300
            size: 50, 50
        
        Mesh:
            vertices: self.l
            indices: self.l2
            mode: 'triangle_fan'
        StencilUse
            func_op: 'lequal'
        Color:
            rgb: 1, 1, 1
        Rectangle:
            pos: 0, 0
            size: 900, 900
            source: 'data/logo/kivy-icon-512.png'
        Color:
            rgb: 1, 0, 0

        StencilUnUse
        Rectangle:
            pos: 300, 300
            size: 50, 50
        Mesh:
            vertices: self.l
            indices: self.l2
            mode: 'triangle_fan'
        StencilPop
''')

class TestStencil(Scatter):
    mposx = NumericProperty(0)
    mposy = NumericProperty(0)
    x1 = NumericProperty(300)
    y1 = NumericProperty(300)
    x2 = 200
    y2 = 400
    x3 = 400
    y3 = 400
    useless = 0.0 # NumericProperty(0.0)

    # l = ReferenceListProperty(x1, y1, useless, useless, x2, y2, useless, useless, x3, y3, useless, useless)
    l2 = ListProperty([0, 1, 2])
    def __init__(self, **kwargs):
        super(TestStencil, self).__init__(**kwargs)
    
    def gettest(self):
        print "gettest called"
        l = [
        self.x1, 
        self.y1, 
        self.useless, 
        self.useless, 
        self.x2, 
        self.y2, 
        self.useless, 
        self.useless, 
        self.x3, 
        self.y3, 
        self.useless, 
        self.useless]
        print l
        return l

    def settest(self, val):
        print "setter called"

    l = AliasProperty(gettest, settest, bind=('x1', 'y1'))
    
    def update(self, useless, **kwargs):
        # print Window.mouse_pos
        h = 100
        w = 100
        mx = Window.mouse_pos[0]
        my = Window.mouse_pos[1]
        self.x2 = mx - w
        self.x3 = mx + w
        self.y2 = my + h
        self.y3 = my + h
        self.mposx = mx
        self.mposy = my
        self.x1 = mx
        self.y1 = my

        self.l2 = range(0, len(self.l))
        # print self.l
        # self.canvas.clear()
        # with self.canvas:
        #     # Color(0, 0, 1)
        #     # Rectangle(pos=(0, 0), size=(900, 900))
            
        #     StencilPush()
        #     Rectangle(pos=(300, 300), size=(50, 50))
        #     Rectangle(pos=(self.mposx-20, self.mposy-20), size=(40, 40))
            
        #     StencilUse(func_op="lequal")
        #     Color(1, 1, 1)
        #     Rectangle(pos=(0, 0), size=(900, 900), source='data/logo/kivy-icon-512.png')
            
        #     StencilUnUse()
        #     Rectangle(pos=(20, 20), size=(50, 50))
        #     Rectangle(pos=(self.mposx-20, self.mposy-20), size=(40, 40))
                        
        #     StencilPop()


class Wid(Widget):
    pass
        


class TestStencilApp(App):
    def build(self):
        # root = StencilView(size_hint=(None, None))
        # root.add_widget(TestStencil())
        self.root = Wid()
        ts = TestStencil()
        self.root.add_widget(ts)
        Clock.schedule_interval(ts.update, 1.0 / 10.0)
        return self.root

TestStencilApp().run()
