#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join
from kivy.app import App
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle, StencilPush, StencilUse, StencilPop, StencilUnUse, Triangle, Line
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory
import sys
import logging
import math

import shapely.geometry
import shapely.ops
from shapely.geometry import Polygon

import network_protocol as np
from client import ClientNetworker
from slmap import SLMap


from kivy.config import Config


map = None
character = None
server = None
logger = None
CELL_SIZE = 32
MAX_MIN_COUNTDOWN = 3
clientNetworker = None
game = None
shadow = None
capInfo = None

class SpylightGame(Widget):
    character = ObjectProperty(None)

    def __init__(self, character, map, **kwargs):
        global shadow, capInfo
        super(SpylightGame, self).__init__(**kwargs)

        self.soundBeep = SoundLoader.load("music/beep.wav")
        self.soundShot = SoundLoader.load("music/shot.wav")
        self.soundReload = SoundLoader.load("music/reload.wav")
        self.soundModem = SoundLoader.load("music/modem.wav")
        self.soundPunch = SoundLoader.load("music/punch.wav")
        self.soundBoom = SoundLoader.load("music/boom.wav")

        self.character = character
        self.add_widget(MapView(map=map, character=self.character, shadow=shadow))
        self.add_widget(character)
        capInfo = CapInfo()
        self.add_widget(capInfo)
        self.started = False

    def update(self, useless, **kwargs):
        self.character.update(kwargs)

    def playBeep(self):
        self.soundBeep.play()

    def playShot(self):
        self.soundShot.play()

    def playReload(self):
        self.soundReaload.play()

    def playModem(self):
        self.soundModem.play()

    def stopModem(self):
        self.soundModem.stop()

    def playPunch(self):
        self.soundPunch.play()

    def playBoom(self):
        self.soundBoom.play()

    def end(self):
        game.playShot()
        print "The mercenary won!"
        sys.exit()

    def start(self):
        timer = Timer()
        game.add_widget(timer)
        Clock.schedule_interval(timer.updateTime, 1)
        self.started = True



class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def getTexture(self,name, size):
        filename = join('art', name+'.png')
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        self.logger.info(filename)
        return texture

    def __init__(self, map, character, shadow):
        self.character = character
        self.shadow = shadow

        super(MapView, self).__init__()
        self.logger = logging.getLogger("SpylightApp")
        self.width = map.width*CELL_SIZE
        self.height = map.height*CELL_SIZE
        self.groundTexture = self.getTexture(name='wall2', size=(CELL_SIZE,CELL_SIZE))

        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    wall = Wall()
                    wall.pos = (x*CELL_SIZE, y*CELL_SIZE)
                    self.add_widget(wall)
                if map.getItem(x,y) == 0:
                    term = Terminal()
                    term.pos = (x*CELL_SIZE, y*CELL_SIZE)
                    self.add_widget(term)



class Character(Widget):
    RESPAWN_TIME = 2 # in seconds
    x1 = NumericProperty(0)
    y1 = NumericProperty(0)
    x2 = NumericProperty(0)
    y2 = NumericProperty(100)
    x3 = NumericProperty(100)
    y3 = NumericProperty(100)
    points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)
    sightPts = ListProperty([])
    sightIndices = ListProperty([])
    sprite = StringProperty(None)
    MAX_SIGHT_DIST = 110
    
    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)

        self.zPressed = False
        self.qPressed = False
        self.sPressed = False
        self.dPressed = False
        self.ePressed = False
        self.velocity = Vector(0,0)
        self.running = False
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        # print 'My keyboard have been closed!'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        pos2 = self.pos
        # Keycode is composed of an integer + a string
        if keycode[1] == 'z'or keycode[1] == 'up':
            self.zPressed = True
        if keycode[1] == 'q'or keycode[1] == 'left':
            self.qPressed = True
        if keycode[1] == 's'or keycode[1] == 'down':
            self.sPressed = True
        if keycode[1] == 'd'or keycode[1] == 'right':
            self.dPressed = True

        if 'shift' in modifiers:
            self.running = True

        return True

    def _on_keyboard_up(self, useless, keycode):

        if keycode[1] == 'z' or keycode[1] == 'up':
            self.zPressed = False
        if keycode[1] == 'q' or keycode[1] == 'left':
            self.qPressed = False
        if keycode[1] == 's' or keycode[1] == 'down':
            self.sPressed = False
        if keycode[1] == 'd' or keycode[1] == 'right':
            self.dPressed = False
        if keycode[1] == 'e':
            self.activate()


        return True

    def activate(self):
        pass


    coeff = 0.8 # occlusion things
    def update(self, useless, **kwargs):
        if game.started:
            maxVelocity = 3
            if self.running:
                maxVelocity = maxVelocity+self.runningBonus

            deceleration = 1
            # print 'update', self.velocity

            if self.zPressed:
                if self.sPressed:
                    self.velocity[1] = 0
                else:
                    self.velocity[1] = maxVelocity
            else:
                 if self.sPressed:
                    self.velocity[1] = -maxVelocity

            if self.qPressed:
                if self.dPressed:
                    self.velocity[0] = 0
                else:
                    self.velocity[0] = -maxVelocity
            else:
                if self.dPressed:
                    self.velocity[0] = maxVelocity

            # print 'velocity ' + str(self.velocity)

            pos2 = self.velocity + self.pos
            if(self.canGo(pos2)):
                self.pos = pos2
            else:
                for i in xrange(0,2):
                    if self.velocity[i] > 0:
                        self.pos[i] -= 1
                    elif self.velocity[i] < 0:
                        self.pos[i] += 1


            for i in xrange(0,2):
                if self.velocity[i] < 0:
                    self.velocity[i] += deceleration
                elif self.velocity[i] > 0:
                    self.velocity[i] -= deceleration

            self.heading = (Vector(*Window.mouse_pos) - Vector(self.center_x, self.center_y)).angle(Vector(0, 1))
            self.x1, self.y1 = self.center_x, self.center_y
            self.x2, self.y2 = Vector(-50, 100).rotate(self.heading) + [self.center_x, self.center_y]
            self.x3, self.y3 = Vector(50, 100).rotate(self.heading) + [self.center_x, self.center_y]
            sight = Polygon([[self.x1, self.y1], [self.x2, self.y2], [self.x3, self.y3]])
            actual_sight = None

            # Occlusion computation

            
            m = (self.x1, self.y1)
            for o in map.walls:
                polygons = []
                x, y = o[0]*CELL_SIZE, o[1]*CELL_SIZE
                # Is this wall potentially colliding with my sight? (is it in the sight range?)
                if (abs(self.center_x - x)-CELL_SIZE) > self.MAX_SIGHT_DIST or (abs(self.center_y - y)-CELL_SIZE) > self.MAX_SIGHT_DIST:
                    # Then, not in sight range, so skip it
                    continue
                coords = [[x, y], [x+CELL_SIZE, y], [x+CELL_SIZE, y+CELL_SIZE], [x, y+CELL_SIZE]]
                l = 4
                i = 0
                while i < l:
                    ind = i
                    ind2 = (i + 1) % l
                    v = Vector([coords[ind][0] - m[0], coords[ind][1] - m[1]]) * self.coeff
                    v2 = Vector([coords[ind2][0] - m[0], coords[ind2][1] - m[1]]) * self.coeff
                    # points = [
                    #     coords[ind][0], coords[ind][1], # obstacle's edge's pt1 
                    #     coords[ind][0] + v[0], coords[ind][1] + v[1], # obstacle's edge's pt1 + v
                    #     coords[ind2][0] + v2[0], coords[ind2][1] + v2[1], # obstacle's edge's pt2 + v2
                    #     coords[ind2][0], coords[ind2][1] # obstacle's edge's pt2
                    #     ]
                    # with self.parent.canvas:
                    #     Color(1,0,0)
                    #     Line(points=points, width=1)
                    points2 = [
                            [ coords[ind][0], coords[ind][1] ], # pt1
                            [ coords[ind][0] + v[0], coords[ind][1] + v[1] ], # pt1 + v
                            [ coords[ind2][0] + v2[0], coords[ind2][1] + v2[1] ], # pt2 + v2
                            [ coords[ind2][0], coords[ind2][1] ] # pt2
                            ]
                    t = Polygon(points2)
                    if t.is_valid:
                        # print "Appending"
                        polygons.append(t)
                    i += 1
                    x = None
                try:
                    x = shapely.ops.cascaded_union(polygons)
                except ValueError as e:
                    print "ValueError Exception when cascaded_union():", e
                    for p in polygons:
                        print "------ polygon ------"
                        for q in p.exterior.coords:
                            print q
                        print "------ polygon ------"
                try:
                    sight = sight.difference(x)
                except ValueError as e:
                    print "ValueError Exception when difference():", e
                    print "x=", x
            final_points = []
            if type(sight) is shapely.geometry.MultiPolygon:
                for s in sight:
                    for (x, y) in s.exterior.coords:
                        final_points.append(x)
                        final_points.append(y)        
            else:
                for (x, y) in sight.exterior.coords:
                    final_points.append(x)
                    final_points.append(y)
            self.sightPts = final_points
            self.sightIndices = range(0, len(self.sightPts))

        if server:
            self.notifyServer()

        self.running = False;
        # print 'Position',self.pos, 'Triangle', self.points

    def canGo(self,pos2):
        margin = 7
        ret = map.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and map.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        logger.debug(pos2, (pos2[0]+margin)/CELL_SIZE,(pos2[1]+margin)/CELL_SIZE)

        return ret

    def notifyServer(self):
        clientNetworker.pos(*self.pos)
        clientNetworker.mouse_pos(*Window.mouse_pos)

        if self.running:
            clientNetworker.run()

        clientNetworker.send()

        self.displayReception()

    def displayReception(self):
        global game
        ret = clientNetworker.recv()

        logger.info(ret)

        logger.info(shadow.pos)

        shadow.pos = ret["ennemy"]

        # capInfo.update(ret["cap"])

        if ret["beep"]:
            game.playBeep()

        if ret["dead"]:
            game.playShot()
            self.pos = (-42, -42)
            Clock.schedule_once(self.spawn, self.RESPAWN_TIME)

            # self.deathLabel = Label("Boom!")
            # addWidget(deathLabel)

        if ret["lost"]:
            sys.exit()

    def spawn(self, dt):
        self.pos = self.spawnPoint


class Spy(Character):
    def __init__(self, **kwargs):
        logger.info('init spy')
        self.sprite = 'art/spy.png'
        self.runningBonus = 12
        self.spawnPoint = (map.spawnPoints[map.SPY_SPAWN][0]*CELL_SIZE, map.spawnPoints[map.SPY_SPAWN][1]*CELL_SIZE)
        self.pos = self.spawnPoint
        super(Spy, self).__init__(**kwargs)
        self.capturing = False

    def update(self, useless, **kwargs):
        if game.started:
            if self.capturing and (self.zPressed or self.qPressed or self.sPressed or self.dPressed):
                self.capturing = False
                game.stopModem()
                if server:
                    clientNetworker.desactivate()
            super(Spy,self).update(useless, **kwargs)
            if self.heading % 360 >= 337.5 or self.heading % 360 < 22.5:
                self.sprite = 'art/spy0.png'
            elif self.heading % 360 >= 22.5 and self.heading % 360 < 67.5:
                self.sprite = 'art/spy315.png'
            elif self.heading % 360 >= 67.5 and self.heading % 360 < 112.5:
                self.sprite = 'art/spy270.png'
            elif self.heading % 360 >= 112.5 and self.heading % 360 < 157.5:
                self.sprite = 'art/spy225.png'
            elif self.heading % 360 >= 157.5 and self.heading % 360 < 202.5:
                self.sprite = 'art/spy180.png'
            elif self.heading % 360 >= 202.5 and self.heading % 360 < 247.5:
                self.sprite = 'art/spy135.png'
            elif self.heading % 360 >= 247.5 and self.heading % 360 < 292.5:
                self.sprite = 'art/spy90.png'
            else:
                self.sprite = 'art/spy45.png'

    def activate(self):
        if game.started:
            super(Spy,self).activate()
            game.playModem()
            self.capturing = True
            logger.info('Spy is activating!')
            if server:
                clientNetworker.activate()


class Mercenary(Character):
    def __init__(self, **kwargs):
        global map
        logger.info('init mercenary')
        self.runningBonus = 0
        self.sprite = 'art/mercenary.png'
        self.spawnPoint = (map.spawnPoints[map.MERCENARY_SPAWN][0]*CELL_SIZE,map.spawnPoints[map.MERCENARY_SPAWN][1]*CELL_SIZE)
        self.pos = self.spawnPoint
        super(Mercenary, self).__init__(**kwargs)

    def update(self, useless, **kwargs):
        if game.started:
            self.running = True
            super(Mercenary,self).update(useless, **kwargs)
            if self.heading % 360 >= 337.5 or self.heading % 360 < 22.5:
                self.sprite = 'art/mercenary0.png'
            elif self.heading % 360 >= 22.5 and self.heading % 360 < 67.5:
                self.sprite = 'art/mercenary315.png'
            elif self.heading % 360 >= 67.5 and self.heading % 360 < 112.5:
                self.sprite = 'art/mercenary270.png'
            elif self.heading % 360 >= 112.5 and self.heading % 360 < 157.5:
                self.sprite = 'art/mercenary225.png'
            elif self.heading % 360 >= 157.5 and self.heading % 360 < 202.5:
                self.sprite = 'art/mercenary180.png'
            elif self.heading % 360 >= 202.5 and self.heading % 360 < 247.5:
                self.sprite = 'art/mercenary135.png'
            elif self.heading % 360 >= 247.5 and self.heading % 360 < 292.5:
                self.sprite = 'art/mercenary90.png'
            else:
                self.sprite = 'art/mercenary45.png'

    def activate(self):
        if game.started:
            super(Mercenary,self).activate()

            logger.info('Mercenary is activating!')
            game.add_widget(Mine(self.center))

            if server:
                clientNetworker.drop(np.OT_MINE)



class Wall(Widget):
    pass


class Terminal(Widget):
    pass


class Shadow(Widget):
    def __init__(self, sprite, **kwargs):
        self.sprite = sprite
        super(Shadow, self).__init__(**kwargs)


class Mine(Widget):
    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10;
        super(Mine, self).__init__(**kwargs)

class CapInfo(Widget):
    percentage = StringProperty("0%")

    def __init__(self, **kwargs):
        super(CapInfo, self).__init__(**kwargs)

    def update(self, newValue):
        self.percentage = str(newValue)+'%'



class Timer(Widget):
    time = StringProperty("00:00")


    def __init__(self, **kwargs):
        self.mins = MAX_MIN_COUNTDOWN
        self.secs = 0
        self.timeToString()
        super(Timer, self).__init__(**kwargs)

    def timeToString(self):
        self.time = '0'+str(self.mins)+':'
        if self.secs < 10:
            self.time += '0' + str(self.secs)
        else:
            self.time += str(self.secs)


    def updateTime(self, useless):
        global game
        self.secs -= 1
        if self.secs == -1:
            self.mins -= 1
            self.secs = 59

        self.timeToString()
        if self.mins == 0 and self.secs == 0:
            game.end()

Factory.register("MapView", MapView)
Factory.register("Shadow", Shadow)


class SpylightApp(App):

    def initLogger(self):
        logger = logging.getLogger("SpylightApp")
        logger.addHandler(logging.FileHandler("spylight.log"))
        logger.setLevel(logging.INFO)
        return logger

    def build(self):
        global map, logger, clientNetworker, game, shadow
        logger = self.initLogger()


        map = SLMap("test.map")
        logger.info("Map loaded: " + map.title)
        logger.info("Map size: (" + str(map.width) + ", " + str(map.height) + ")")

        logger.info("What in (4, 8): " + str(map.getItem(4, 8)))

        if character == 'merc':
            char = Mercenary()
            shadow = Shadow('art/spy.png')
            if server:
                clientNetworker = ClientNetworker(np.MERCENARY_TYPE)
        else:
            char = Spy()
            shadow = Shadow('art/mercenary.png')
            if server:
                clientNetworker = ClientNetworker(np.SPY_TYPE)

        if server:
            clientNetworker.connect(server, 9999)

        game = SpylightGame(character=char, map=map)

        Clock.schedule_interval(game.update, 1.0 / 20.0)

        game.start()

        return game

if __name__ == '__main__':
    global character, server

    if len(sys.argv) >= 2:
        character = sys.argv[1]

    if len(sys.argv) >= 3:
        server = sys.argv[2]

    SpylightApp().run()
