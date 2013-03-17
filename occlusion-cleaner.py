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

Builder.load_string('''
<BlorgWidget>:
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
            rgb: 0, 0, 1
        Rectangle:
            pos: 0, 0
            size: 900, 900
        Color:
            rgb: 1, 0, 0
        Rectangle:
            pos: 300, 320
            size: 20, 20
        
        Rectangle:
            pos: 500, 530
            size: 20, 20

        Rectangle:
            pos: 300, 270
            size: 20, 20

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

class BlorgWidget(Widget):
    """docstring for BlorgWidget"""
    x1 = NumericProperty(300)
    y1 = NumericProperty(300)

    sight_points = []
    l2 = ListProperty([])

    def gettest(self):
        if DBG:
            print "gettest called"
            print self.sight_points
        return self.sight_points

    def settest(self, val):
        if DBG:
            print "setter called"

    l = AliasProperty(gettest, settest, bind=('x1', 'y1'))
    
    def __init__(self, **args):
        super(BlorgWidget, self).__init__(**args)
        
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
        self.obs_pos = obs
        self.obs = []
        for p in self.obs_pos:
            poly = Polygon([[p[0], p[1]], [p[0] + self.w, p[1]], [p[0] + self.w, p[1] + self.h], [p[0], p[1] + self.h] ])
            self.obs.append(poly)

    def setAlliesSights(self, sightsList):
        self.allies = sightsList

    def setEnnemies(self, ennemies):
        self.dudes = ennemies

    def compute(self):
        m = Vector([self.mpos_x, self.mpos_y])
        sight = Polygon([[self.mpos_x, self.mpos_y], [self.mpos_x - 100, self.mpos_y + 200], [self.mpos_x + 100, self.mpos_y + 200]])
        poly_union = None
        polygons = []
        color_index = -50

        for o in self.obs:
            color_index += 50
            l = len(o.exterior.coords)
            i = 0
            while i < l:
                ind = i
                ind2 = (i + 1) % l
                v = Vector([o.exterior.coords[ind][0] - m[0], o.exterior.coords[ind][1] - m[1]]) * self.coeff
                v2 = Vector([o.exterior.coords[ind2][0] - m[0], o.exterior.coords[ind2][1] - m[1]]) * self.coeff
                points = [
                        o.exterior.coords[ind][0], o.exterior.coords[ind][1], # obstacle's edge's pt1 
                        o.exterior.coords[ind][0] + v[0], o.exterior.coords[ind][1] + v[1], # obstacle's edge's pt1 + v
                        o.exterior.coords[ind2][0] + v2[0], o.exterior.coords[ind2][1] + v2[1], # obstacle's edge's pt2 + v2
                        o.exterior.coords[ind2][0], o.exterior.coords[ind2][1] # obstacle's edge's pt2
                        ]
                points2 = [
                        [ o.exterior.coords[ind][0], o.exterior.coords[ind][1] ], # pt1
                        [ o.exterior.coords[ind][0] + v[0], o.exterior.coords[ind][1] + v[1] ], # pt1 + v
                        [ o.exterior.coords[ind2][0] + v2[0], o.exterior.coords[ind2][1] + v2[1] ], # pt2 + v2
                        [ o.exterior.coords[ind2][0], o.exterior.coords[ind2][1] ] # pt2
                        ]
                t = Polygon(points2)
                if t.is_valid:
                    polygons.append(t)
                i += 1
            # /while
            union = None
            try:
                union = shapely.ops.cascaded_union(polygons)
            except ValueError as e:
                print "ValueError Exception when cascaded_union():", e
                # for p in polygons:
                #     print "------ polygon ------"
                #     for q in p.exterior.coords:
                #         print q
                #     print "------ polygon ------"
        # /for o in self.obs
        try:
            sight = sight.difference(union)
        except ValueError as e:
            print "ValueError Exception when difference():", e
            sight = Polygon([[0,0], [1,1], [2,2]])
        blorg_points = []
        final_points = []
        max = 0
        for (x, y) in sight.exterior.coords:
            final_points.append(x)
            final_points.append(y)
            blorg_points.extend((x, y, 0.0, 0.0))
            max += 1

        self.vertices = blorg_points
        self.indices = range(0, len(self.vertices)/4)
        
class MeshTestApp(App):
    coeff = 20.0
    FPS=2

    def draw_obs(self, dt):
        mpos_x, mpos_y = int(Window.mouse_pos[0]), int(Window.mouse_pos[1])
        self.s.setMousePos(mpos_x, mpos_y)
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
        self.s.setEnnemies([(500, 530), (300, 270), (300, 330)])
        
        layout = BoxLayout(size_hint=(1, None), height=50)
        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)
        
        Clock.schedule_interval(self.draw_obs, 1.0/self.FPS)
        
        return root

if __name__ == '__main__':
    MeshTestApp().run()
