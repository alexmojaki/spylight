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

class MeshTestApp(App):
    coeff = 0.8
    def draw_obs(self, dt):
        self.wid.canvas.clear()
        self.mpos_x = int(Window.mouse_pos[0])
        self.mpos_y = int(Window.mouse_pos[1])
        
        w = 20
        h = 20
        # self.obs_pos = [(500, 500), (40, 40), (100, 100), (200, 200), (300, 300)]
        self.obs_pos = [(500, 500)]
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
        scene = Polygon([[0,0], [0, Window.height], [Window.width, Window.height], [Window.width, 0]])
        sight = scene
        poly_union = None
        polygons = []
        for o in self.obs:
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
                print "Interior polygon:", Polygon(points2)
                polygons.append(Polygon(points2))
                # with self.wid.canvas:
                #     Color(0,1,0)
                    # Line(points=points, width=1)
                    # Quad(points=points)
                i += 1
                with self.wid.canvas:
                    Color(1,0,0)
                    Line(points=points, width=1)

            try:
                sight = sight.difference(shapely.ops.cascaded_union(polygons))
            except ValueError as e:
                print "ValueError Exception:", e
                sight = Polygon([[0,0], [1,1], [2,2]])
            final_points = []
            for (x, y) in sight.exterior.coords:
                final_points.append(x)
                final_points.append(y)
            final_points2 = []
            for u in sight.interiors:
                for (x, y) in u.coords:
                    final_points2.append(x)
                    final_points2.append(y)

            # print "Exterior:", final_points
            # print "Interiors:", final_points2
            print "==========================", points, "======================="
            with self.wid.canvas:
                # Color(1,0,0)
                # Line(points=points, width=1)
                Color(0,1,0)
                Line(points=final_points, width=3)
                Line(points=final_points2, width=3)


        # Note : We draw the obstacle themselves after the sight's shadow's polygons in order to get them visible and not under those polygons
        for p in self.obs_pos:
            with self.wid.canvas:
                Color(1,1,0)
                # self.mesh = Mesh(vertices=coords, indices=list(range(0, 4)), mode = "triangle_fan")
                Rectangle(pos=p, size=(w, h))

    def build(self):
        self.wid = wid = Widget()
        
        layout = BoxLayout(size_hint=(1, None), height=50)
        # for mode in ('points', 'line_strip', 'line_loop', 'lines',
        #         'triangle_strip', 'triangle_fan'):
        #     button = Button(text=mode)
        #     button.bind(on_release=partial(self.change_mode, mode))
        #     layout.add_widget(button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        
        Clock.schedule_interval(self.draw_obs, 0.08)

        return root

if __name__ == '__main__':
    MeshTestApp().run()
