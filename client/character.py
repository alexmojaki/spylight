import sys

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.vector import Vector
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

# from client.network import ClientNetworker
from client import utils
import common.network_protocol as np
import common.game_constants as c

Builder.load_string('''
<Character>:
    size: 32,32
    rotation: 0
    # collisionBox: collisionBox

    Scatter:
        id:scatter
        do_translation: False, False
        do_rotation: False
        do_scale: False
        # size: root.size  # Don't use size! use scale instead (cf Scatter's doc)
        center: root.center
        rotation: root.rotation
        scale: 1.68  # 32/19

        Image:
            source: root.sprite

    # Widget:
    #     id: collisionBox
    #     size: 25,25
    #     center: root.center

''')

_teams = [
    {'name': 'spy', 'sprite': utils.spritePath.format('spy')},
    {'name': 'mercenary', 'sprite': utils.spritePath.format('mercenary')}
]


class Character(Widget):
    offsetx = NumericProperty(0)
    offsety = NumericProperty(0)
    offset = ReferenceListProperty(offsetx, offsety)

    def __init__(self, team, init_pos, on_new_offset_callback):
        self.screenpos = Window.size[0]/2, Window.size[1]/2
        self.center = self.screenpos
        self.sprite = _teams[team]['sprite']
        self.bind(offset=on_new_offset_callback)
        self.set_game_pos(init_pos)
        super(Character, self).__init__()

    def set_game_pos(self, pos):
        self.gamepos = pos
        self.update_offset()

    def update_offset(self):
        self.offsetx = self.screenpos[0] - self.gamepos[0]
        self.offsety = self.screenpos[1] - self.gamepos[1]

# clientNetworker = None


# class Character(Widget):
#     x1 = NumericProperty(0)
#     y1 = NumericProperty(0)
#     x2 = NumericProperty(0)
#     y2 = NumericProperty(100)
#     x3 = NumericProperty(100)
#     y3 = NumericProperty(100)
#     points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)
#     sprite = StringProperty(None)

#     def __init__(self, game, cellMap, **kwargs):
#         # Builder.load_file('kv/character.kv')
#         super(Character, self).__init__(**kwargs)
#         Logger.info('SL|Character: size at creation: %s', self.size)

#         # Only used to test w/o starting a server
#         self.server = kwargs.get('self.server', None)

#         self.game = game
#         self.cellMap = cellMap
#         self.upPressed = False
#         self.leftPressed = False
#         self.downPressed = False
#         self.rightPressed = False
#         self.actionPressed = False
#         self.velocity = Vector(0, 0)
#         self.running = False

#     # Keyboard events: set the related value to false on keyup, true on keydown
#     def upEvt(self, instance, value):
#         self.upPressed = value

#     def leftEvt(self, instance, value):
#         self.leftPressed = value

#     def downEvt(self, instance, value):
#         self.downPressed = value

#     def rightEvt(self, instance, value):
#         self.rightPressed = value

#     def actionEvt(self, instance, value):
#         self.actionPressed = value
#         if value:  # keydown only
#             self.activate()

#     def runEvt(self, instance, value):
#         self.running = value

#     def activate(self):
#         pass

#     def update(self):
#         Logger.debug('SL|Character: size: %s', self.size)
#         maxVelocity = 3
#         if self.running:
#             maxVelocity = maxVelocity+self.runningBonus

#         deceleration = 1

#         if self.upPressed:
#             if self.downPressed:
#                 self.velocity[1] = 0
#             else:
#                 self.velocity[1] = maxVelocity
#         else:
#             if self.downPressed:
#                 self.velocity[1] = -maxVelocity

#         if self.leftPressed:
#             if self.rightPressed:
#                 self.velocity[0] = 0
#             else:
#                 self.velocity[0] = -maxVelocity
#         else:
#             if self.rightPressed:
#                 self.velocity[0] = maxVelocity

#         pos2 = self.velocity + self.pos

#         # alt: collision vs char's collision box and viewMap's impassable list
#         if(self.canGo(pos2)):
#             self.pos = pos2
#         else:
#             for i in xrange(0, 2):
#                 if self.velocity[i] > 0:
#                     self.pos[i] -= 1
#                 elif self.velocity[i] < 0:
#                     self.pos[i] += 1

#         for i in xrange(0, 2):
#             if self.velocity[i] < 0:
#                 self.velocity[i] += deceleration
#             elif self.velocity[i] > 0:
#                 self.velocity[i] -= deceleration

#         self.heading = (Vector(*Window.mouse_pos) - Vector(self.center_x, self.center_y)).angle(Vector(0, 1))
#         self.x1, self.y1 = self.center_x, self.center_y
#         self.x2, self.y2 = Vector(-50, 100).rotate(self.heading) + [self.center_x, self.center_y]
#         self.x3, self.y3 = Vector(50, 100).rotate(self.heading) + [self.center_x, self.center_y]

#         if self.server:
#             self.notifyServer()

#         self.running = False
#         self.rotation = self.heading  # Rotates the sprite

#     def canGo(self, pos2):
#         margin = 7
#         ret = self.cellMap.getWallType((pos2[0]+margin)/c.CELL_SIZE, (pos2[1]+margin)/c.CELL_SIZE) == -1
#         ret = ret and self.cellMap.getWallType((pos2[0]+c.CELL_SIZE-margin)/c.CELL_SIZE, (pos2[1]+c.CELL_SIZE-margin)/c.CELL_SIZE) == -1
#         ret = ret and self.cellMap.getWallType((pos2[0]+margin)/c.CELL_SIZE, (pos2[1]+c.CELL_SIZE-margin)/c.CELL_SIZE) == -1
#         ret = ret and self.cellMap.getWallType((pos2[0]+c.CELL_SIZE-margin)/c.CELL_SIZE, (pos2[1]+margin)/c.CELL_SIZE) == -1

#         return ret

#     def notifyServer(self):
#         clientNetworker.pos(*self.pos)
#         clientNetworker.mouse_pos(*Window.mouse_pos)

#         if self.running:
#             clientNetworker.run()

#         clientNetworker.send()

#         self.displayReception()

#     def displayReception(self):
#         ret = clientNetworker.recv()

#         shadow.pos = ret["ennemy"]

#         if ret["cap"] > -1:
#             # capInfo.update(ret["cap"])
#             self.game.playModem()

#         if ret["beep"]:
#             self.game.playBeep()

#         if ret["dead"]:
#             self.game.playShot()
#             self.pos = (-42, -42)
#             Clock.schedule_once(self.spawn, c.RESPAWN_TIME)

#             # self.deathLabel = Label("Boom!")
#             # addWidget(deathLabel)

#         if ret["lost"]:
#             sys.exit()

#     def spawn(self, dt):
#         self.pos = self.spawnPoint


# ### SPY #######################################################################
# class Spy(Character):
#     name = 'spy'
#     sprite = utils.spritePath.format('spy')

#     def __init__(self, game, cellMap, **kwargs):
#         self.runningBonus = 12
#         self.spawnPoint = (
#             cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][0]*c.CELL_SIZE,
#             cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][1]*c.CELL_SIZE)
#         self.pos = self.spawnPoint
#         super(Spy, self).__init__(game, cellMap, **kwargs)
#         self.capturing = False

#     def update(self):
#         if self.game.started:
#             if self.capturing:
#                 if self.upPressed or self.leftPressed or self.downPressed or self.rightPressed:
#                     self.capturing = False
#                     # capInfo.update(0)
#                     self.game.stopModem()
#                 elif self.server:
#                     clientNetworker.activate()

#             super(Spy, self).update()

#     def activate(self):
#         Logger.info('SL|Spy: Activating!')
#         if self.game.started:
#             self.capturing = True
#             if self.server:
#                 clientNetworker.activate()


# ### MERCENARY #################################################################

# class Mercenary(Character):
#     name = 'merc'
#     sprite = utils.spritePath.format('mercenary')

#     def __init__(self, game, cellMap, **kwargs):
#         Logger.info('SL|Mercenary: init')
#         self.runningBonus = 0
#         self.spawnPoint = (
#             cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][0]*c.CELL_SIZE,
#             cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][1]*c.CELL_SIZE)
#         self.pos = self.spawnPoint
#         super(Mercenary, self).__init__(game, cellMap, **kwargs)
#         self.mines = dict()

#     def update(self):
#         if self.game.started:
#             self.running = True
#             super(Mercenary, self).update()

#     def activate(self):
#         if self.game.started:
#             super(Mercenary, self).activate()

#             Logger.info('SL|Mercenary: Activating!')
#             if not self.mines in str(self.center):
#                 mw = Mine(self.center)
#                 self.mines[str(self.center)] = mw
#                 self.game.add_widget(mw)

#             if self.server:
#                 clientNetworker.drop(np.OT_MINE)

#     def displayReception(self):
#         super(Mercenary, self).displayReception()

#         if ret["boom"]:
#             self.game.remove_widget(self.mines.pop(str([0, 0])))
