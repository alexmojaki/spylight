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
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, ObjectProperty, StringProperty, AliasProperty 
# from functools import partial
# from math import cos, sin, pi
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.lang import Builder

import shapely.geometry
import shapely.ops
from shapely.geometry import Polygon

DBG = False

from time import time
from shapely.occlusion import occlusion

Builder.load_string('''
<BlorgWidget>:
    canvas:
        StencilPush
        # This is a spotlight
        Rectangle:
            pos: 300, 300
            size: 50, 50
        
        # sight view
        Mesh:
            vertices: self.l
            indices: self.l2
            mode: 'triangle_fan'
        StencilUse
            func_op: 'lequal'

        Color:
            rgb: 0, 0, 1
        Rectangle:
            pos: 0, 0
            size: 900, 900
        Color:
            rgb: 1, 0, 0
        # Those are the ennemies
        Rectangle:
            pos: 300, 320
            size: 20, 20
        
        Rectangle:
            pos: self.moving_ennemy_x, 530
            size: 20, 20

        Rectangle:
            pos: 300, 270
            size: 20, 20

        StencilUnUse
        # This is a spotlight
        Rectangle:
            pos: 300, 300
            size: 50, 50
        # sight view
        Mesh:
            vertices: self.l
            indices: self.l2
            mode: 'triangle_fan'
        StencilPop
''')

class BlorgWidget(Widget):
    """docstring for BlorgWidget"""
    x1 = NumericProperty(300)
    y1 = NumericProperty(300)
    moving_ennemy_x = NumericProperty(500)

    sight_points = []
    l2 = ListProperty([])

    def __init__(self, **args):
        super(BlorgWidget, self).__init__(**args)
        self.moving_ennemy_x = 500

    def gettest(self):
        if DBG:
            print "gettest called"
            print self.sight_points
        return self.sight_points

    def settest(self, val):
        if DBG:
            print "setter called"

    l = AliasProperty(gettest, settest, bind=('x1', 'y1'))
    

        
class SightView(object):
    """docstring for SightView"""
    def __init__(self):
        super(SightView, self).__init__()

class PolygonSightView(SightView):
    """SightView for a Polygonal view"""
    coeff = 20.0
    w = 20
    h = 20
    def __init__(self, polygon):
        super(PolygonSightView, self).__init__()
        self.polygon = polygon

    def setMousePos(self, x, y):
        self.mpos_x = x
        self.mpos_y = y

    def getPoints(self):
        if DBG:
            print "#c01"
        result = {"vertices": self.vertices, "indices": self.indices}
        if DBG:
            print "#c02", result
        return result

    def setObstacles(self, obs):
        self.obs = []
        self.obs_n = 0
        for p in obs:
            self.obs.extend(
            [p[0], p[1],
            p[0] + self.w, p[1],
            p[0] + self.w, p[1] + self.h, 
            p[0], p[1] + self.h])
            self.obs_n += 8
        print self.obs

    def setAlliesSights(self, sightsList):
        self.allies = sightsList

    def setEnnemies(self, ennemies):
        self.dudes = ennemies

    def compute(self):
        self.vertices = occlusion(self.mpos_x, self.mpos_y, self.obs, self.obs_n)
        self.indices = range(0, len(self.vertices)/4)
        
class MeshTestApp(App):
    FPS=100
    def draw_obs(self, dt):
        # from time import time
        
        mpos_x, mpos_y = int(Window.mouse_pos[0]), int(Window.mouse_pos[1])
        self.s.setMousePos(mpos_x, mpos_y)
        self.wid.moving_ennemy_x = (self.wid.moving_ennemy_x + 30) % 700
        self.s.setEnnemies([(self.wid.moving_ennemy_x, 530), (300, 270), (300, 330)])
        self.s.compute()

        p = self.s.getPoints()
        self.wid.sight_points = p["vertices"]
        self.wid.x1 = mpos_x
        self.wid.y1 = mpos_y
        self.wid.l2 = p["indices"]
        
    def build(self):
        self.wid = wid = BlorgWidget()
        self.s = PolygonSightView(None) # @todo
        self.s.setObstacles([(500, 500), (40, 40), (100, 100), (200, 200), (300, 300)])
        
        layout = BoxLayout(size_hint=(1, None), height=50)
        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)
        
        Clock.schedule_interval(self.draw_obs, 1.0/self.FPS)
        
        return root

if __name__ == '__main__':
    MeshTestApp().run()
