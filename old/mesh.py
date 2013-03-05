#!/usr/bin/python

'''
Mesh test
=========

'''

from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Mesh
from functools import partial
from math import cos, sin, pi
from kivy.core.window import Window

import shapely.geometry

class MeshTestApp(App):

    def change_mode(self, mode, *largs):
        self.mesh.mode = mode

    def build_mesh(self, mask):
        vertices = []
        indices = []
        step = 10
        istep = (pi * 2) / float(step)
        polyList = []
        for i in xrange(step):
            x = 300 + cos(istep * i) * 100
            y = 300 + sin(istep * i) * 100
            polyList.append([x, y])
        # print "\n\n\n\n========\n\n\n\n", vertices
        # print "\n\n\n\n========\n\n\n\n", indices

        orig_x = 100
        orig_y = 100
        circle = shapely.geometry.Polygon([[0,0], [0, Window.height], [Window.width, Window.height], [Window.width, 0]])
        hexa = shapely.geometry.Polygon(polyList)
        print Window.width, ",", Window.height, Window.size
        # rect = shapely.geometry.Polygon([[0, 0], [0, 300], [300, 300], [300, 0]])
        # rect2 = shapely.geometry.Polygon([[0, 300], [0, 600], [600, 600], [600, 300]])
        shape = circle.difference(hexa).difference(mask)
        # shape = mask
        # shape = shapely.geometry.Polygon([[orig_x, orig_y], [orig_x + 200,orig_y + 200], [orig_x + 200, orig_y], [orig_x + 300, orig_y + 200]])
        i = 1
        print shape
        print "\n\n==================\n\n"
        for v in list(shape.exterior.coords):
            print v
            vertices.extend([v[0], v[1], 0, 0])
            indices.append(i-1)
            i += 1
        for u in shape.interiors:
            for v in u.coords:
                vertices.extend([v[0], v[1], 0, 0])
                indices.append(i-1)
                i += 1

        print "\n\n==================\n\n"
        # clip_poly = shapely.geometry.Polygon([[-9.5, -2], [2, 2], [3, 4], [-1, 3]])
        # clipped_shape = circle.difference(clip_poly)

        return Mesh(vertices=vertices, indices=indices)

    def build(self):
        self.wid = wid = Widget()
        maskBotRight = shapely.geometry.Polygon([[0,0], [300, 0], [300,300], [Window.width, 300], [Window.width, Window.height], [0, Window.height]])
        maskBotLeft = shapely.geometry.Polygon([[Window.width, Window.height], [0, Window.height], [0, 300], [300, 300], [300, 0], [Window.width, 0]])
        maskTopRight = shapely.geometry.Polygon([[0,0], [0, Window.height], [300, Window.height], [300, 300], [Window.width, 300], [Window.width, 0]])
        maskTopLeft = shapely.geometry.Polygon([[Window.width, 0], [Window.width, Window.height], [300, Window.height], [300, 300], [0, 300], [0, 0]])
        with wid.canvas:
            self.mesh = self.build_mesh(maskBotRight)
            self.mesh.mode = "triangle_fan"
            self.mesh2 = self.build_mesh(maskTopLeft)
            self.mesh2.mode = "triangle_fan"
            self.mesh3 = self.build_mesh(maskBotLeft)
            self.mesh3.mode = "triangle_fan"
            self.mesh4 = self.build_mesh(maskTopRight)
            self.mesh4.mode = "triangle_fan"

        layout = BoxLayout(size_hint=(1, None), height=50)
        for mode in ('points', 'line_strip', 'line_loop', 'lines',
                'triangle_strip', 'triangle_fan'):
            button = Button(text=mode)
            button.bind(on_release=partial(self.change_mode, mode))
            layout.add_widget(button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        return root

if __name__ == '__main__':
    MeshTestApp().run()
