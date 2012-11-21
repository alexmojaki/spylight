#!/usr/bin/python

'''
Mesh test
=========

'''

# from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle, Line, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle
from kivy.graphics import Mesh, Quad
# from functools import partial
# from math import cos, sin, pi
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector

import shapely.geometry
import shapely.ops
from shapely.geometry import Polygon

from kivy.lang import Builder
from random import randint
import random
random.seed()

Builder.load_string('''
<MyWidget>:
    canvas:
        Mesh:
            vertices: self.vertices
            indices: self.indices
            mode: 'triangle_fan'
''')

class MyWidget(Widget):
    """docstring for MyWidget"""
    vertices = ListProperty([])
    indices = ListProperty([])
    def __init__(self):
        super(MyWidget, self).__init__()

    def update(self):
        vertices.append(randint() % 300)
        vertices.append(randint() % 300)
        indices = range(0, len(indices) + 2)

class MeshTestApp(App):
    coeff = 0.8        

    def build(self):
        self.wid = wid = MyWidget()
        
        layout = BoxLayout(size_hint=(1, None), height=50)
        # for mode in ('points', 'line_strip', 'line_loop', 'lines',
        #         'triangle_strip', 'triangle_fan'):
        #     button = Button(text=mode)
        #     button.bind(on_release=partial(self.change_mode, mode))
        #     layout.add_widget(button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        
        Clock.schedule_interval(wid.update, 0.5)

        return root

if __name__ == '__main__':
    MeshTestApp().run()
