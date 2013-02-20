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
        print "gettest called"
        print self.sight_points
        return self.sight_points

    def settest(self, val):
        print "setter called"

    l = AliasProperty(gettest, settest, bind=('x1', 'y1'))
    
    def __init__(self, **args):
        super(BlorgWidget, self).__init__(**args)
        

class MeshTestApp(App):
    coeff = 20.0
    def draw_obs(self, dt):
        # self.wid.canvas.clear()
        self.mpos_x = int(Window.mouse_pos[0])
        self.mpos_y = int(Window.mouse_pos[1])
        
        w = 20
        h = 20
        self.obs_pos = [(500, 500), (40, 40), (100, 100), (200, 200), (300, 300)]
        self.dudes = [(500, 530), (300, 270), (300, 330)]
        # self.obs_pos = [(300, 250), (250, 250)]
        # print self.obs_pos
        self.obs = []

        for p in self.obs_pos:
            # print p
            poly = Polygon([[p[0], p[1]], [p[0] + w, p[1]], [p[0] + w, p[1] + h], [p[0], p[1] + h] ])
            # coords = [p[0], p[1], 0.0, p[0] + w, p[1], 0.0, p[0] + w, p[1] + h, 0.0, p[0], p[1] + h, 0.0]
            self.obs.append(poly)
            # print coords

        # maskTopLeft = shapely.geometry.Polygon([[Window.width, 0], [Window.width, Window.height], [self.mpos_x, Window.height], [self.mpos_x, self.mpos_y], [0, self.mpos_y], [0, 0]])
        m = Vector([self.mpos_x, self.mpos_y])
        # scene = Polygon([[0,0], [0, Window.height], [Window.width, Window.height], [Window.width, 0]])
        scene = Polygon([[self.mpos_x, self.mpos_y], [self.mpos_x - 100, self.mpos_y + 200], [self.mpos_x + 100, self.mpos_y + 200]])
        sight = scene
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
                # print "coord i=", o.exterior.coords[ind]
                # print "coord i+1=", o.exterior.coords[ind2]
                v = Vector([o.exterior.coords[ind][0] - m[0], o.exterior.coords[ind][1] - m[1]]) * self.coeff
                v2 = Vector([o.exterior.coords[ind2][0] - m[0], o.exterior.coords[ind2][1] - m[1]]) * self.coeff
                # print "v=", v
                # print "v2=", v2
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
                # print "Interior polygon:", Polygon(points2)
                t = Polygon(points2)
                if t.is_valid:
                    polygons.append(t)
                # with self.wid.canvas:
                #     Color(0,1,0)
                    # Line(points=points, width=1)
                    # Quad(points=points)
                i += 1
                # Uncomment the following line in order to view the boxes generated for each edge
                # with self.wid.canvas:
                #     Color(1,0,0)
                #     Line(points=points, width=1)

            union = None
            try:
                union = shapely.ops.cascaded_union(polygons)
            except ValueError as e:
                print "ValueError Exception when cascaded_union():", e
                for p in polygons:
                    print "------ polygon ------"
                    for q in p.exterior.coords:
                        print q
                    print "------ polygon ------"
            # Debugging purpose
            # points = []
            # print "##Union##", union
            # for (x, y) in union.exterior.coords:
            #     points.append(x)
            #     points.append(y)

        try:
            sight = sight.difference(union)
        except ValueError as e:
            print "ValueError Exception when difference():", e
            print union
            print sight
            sight = Polygon([[0,0], [1,1], [2,2]])
        blorg_points = []
        final_points = []
        max = 0
        for (x, y) in sight.exterior.coords:
            final_points.append(x)
            final_points.append(y)
            blorg_points.extend((x, y, 0.0, 0.0))
            max += 1
        final_points2 = []
        # Don't know if this is useful or not, to be tested:
        for u in sight.interiors:
            for (x, y) in u.coords:
                final_points2.append(x)
                final_points2.append(y)

        # print "Exterior:", final_points
        # print "Interiors:", final_points2
        # print "==========================", points, "======================="

        # print blorg_points
        red = (1, 0, 0)
        blue = (0, 0, 1)
        green = (0, 1, 0)
        self.wid.sight_points = blorg_points
        self.wid.x1 = self.mpos_x
        self.wid.y1 = self.mpos_y
        self.wid.l2 = range(0, len(self.wid.sight_points)/4)
        # with self.wid.canvas:
        #     StencilPush()
        #     # Our sight
        #     Rectangle(pos=(300, 130), size=(20, 20))
        #     self.mesh = Mesh(vertices=blorg_points, indices=list(range(0, max)), mode = "triangle_fan")

        #     StencilUse(func_op='lequal')
        #     # The true color of things, in the light...
        #     Color(*blue)
        #     Rectangle(size=(900, 900))
        #     Color(rgba=(0, 0, 0, 255.0))
        #     # And the people that is hiding in the dark!
        #     Color(*red)
        #     Rectangle(pos=(300, 230), size=(20, 20))
        #     Rectangle(pos=(300, 270), size=(20, 20))

        #     StencilUnUse()
        #     # Same instruction as in StencilPush()
        #     Rectangle(pos=(300, 130), size=(20, 20))
        #     self.mesh = Mesh(vertices=blorg_points, indices=list(range(0, max)), mode = "triangle_fan")
            
        #     StencilPop()


        # Note : We draw the obstacle themselves after the sight's shadow's polygons in order to get them visible and not under those polygons
        for p in self.obs_pos:
            with self.wid.canvas:
                Color(1,1,0)
                # self.mesh = Mesh(vertices=coords, indices=list(range(0, 4)), mode = "triangle_fan")
                Rectangle(pos=p, size=(w, h))
        # for p in self.dudes:
        #     with self.wid.canvas:
        #         Color(*red)
        #         Rectangle(pos=p, size=(w, h))

    def build(self):
        self.wid = wid = BlorgWidget()
        
        layout = BoxLayout(size_hint=(1, None), height=50)
        # for mode in ('points', 'line_strip', 'line_loop', 'lines',
        #         'triangle_strip', 'triangle_fan'):
        #     button = Button(text=mode)
        #     button.bind(on_release=partial(self.change_mode, mode))
        #     layout.add_widget(button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        
        Clock.schedule_interval(self.draw_obs, 0.05)

        return root

if __name__ == '__main__':
    MeshTestApp().run()
