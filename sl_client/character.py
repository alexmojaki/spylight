from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.vector import Vector

import network_protocol as np
from client import ClientNetworker as clientNetworker
# from slmap import SLMap
from constants import CELL_SIZE

import custom_logger as c

class Character(Widget):
    x1 = NumericProperty(0)
    y1 = NumericProperty(0)
    x2 = NumericProperty(0)
    y2 = NumericProperty(100)
    x3 = NumericProperty(100)
    y3 = NumericProperty(100)
    points = ReferenceListProperty(x1, y1, x2, y2, x3, y3)
    sprite = StringProperty(None)

    def __init__(self, game, cellMap, **kwargs):
        super(Character, self).__init__(**kwargs)

        # Only used to test w/o starting a server
        self.server = kwargs.get('self.server',None)

        self.game = game
        self.cellMap = cellMap
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


    def update(self, useless, **kwargs):
        maxVelocity = 3
        if self.running:
            maxVelocity = maxVelocity+self.runningBonus

        deceleration = 1

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

        if self.server:
            self.notifyServer()

        self.running = False;

    def canGo(self,pos2):
        margin = 7
        ret = self.cellMap.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        ret = ret and self.cellMap.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and self.cellMap.getWallType((pos2[0]+margin)/CELL_SIZE, (pos2[1]+CELL_SIZE-margin)/CELL_SIZE) == -1
        ret = ret and self.cellMap.getWallType((pos2[0]+CELL_SIZE-margin)/CELL_SIZE, (pos2[1]+margin)/CELL_SIZE) == -1
        c.logger.debug(pos2, (pos2[0]+margin)/CELL_SIZE,(pos2[1]+margin)/CELL_SIZE)

        return ret

    def notifyServer(self):
        clientNetworker.pos(*self.pos)
        clientNetworker.mouse_pos(*Window.mouse_pos)

        if self.running:
            clientNetworker.run()


        clientNetworker.send()

        self.displayReception()

    def displayReception(self):
        ret = clientNetworker.recv()

        shadow.pos = ret["ennemy"]

        if ret["cap"] > -1:
            capInfo.update(ret["cap"])
            self.game.playModem()
            

        if ret["beep"]:
            self.game.playBeep()

        if ret["dead"]:
            self.game.playShot()
            self.pos = (-42, -42)
            Clock.schedule_once(self.spawn, self.RESPAWN_TIME)

            # self.deathLabel = Label("Boom!")
            # addWidget(deathLabel)

        if ret["lost"]:
            sys.exit()

    def spawn(self, dt):
        self.pos = self.spawnPoint

### SPY #######################################################################

class Spy(Character):

    def __init__(self, game, cellMap, **kwargs):
        self.sprite = 'art/spy.png'
        self.runningBonus = 12
        self.spawnPoint = (
            cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][0]*CELL_SIZE,
            cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][1]*CELL_SIZE
            )
        self.pos = self.spawnPoint
        super(Spy, self).__init__(game, cellMap, **kwargs)
        self.capturing = False


    def update(self, useless, **kwargs):
        if self.game.started:
                
            if self.capturing:
                if self.zPressed or self.qPressed or self.sPressed or self.dPressed:
                    self.capturing = False
                    capInfo.update(0)
                    self.game.stopModem()
                elif self.server:
                    clientNetworker.activate()                        

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
        if self.game.started:
            self.capturing = True
            c.logger.info('Spy is activating!')
            if self.server:
                clientNetworker.activate()


### MERCENARY #################################################################

class Mercenary(Character):

    def __init__(self, game, cellMap, **kwargs):
        c.logger.info('init mercenary')
        self.runningBonus = 0
        self.sprite = 'art/mercenary.png'
        self.spawnPoint = (
            cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][0]*CELL_SIZE,
            cellMap.spawnPoints[cellMap.MERCENARY_SPAWN][1]*CELL_SIZE
            )
        self.pos = self.spawnPoint
        super(Mercenary, self).__init__(game, cellMap, **kwargs)
        self.mines = dict()


    def update(self, useless, **kwargs):
        if self.game.started:
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
        if self.game.started:
            super(Mercenary,self).activate()

            c.logger.info('Mercenary is activating!')
            if not self.mines.has_key(str(self.center)):
                mw = Mine(self.center)
                self.mines[str(self.center)] = mw
                self.game.add_widget(mw)

            if self.server:
                clientNetworker.drop(np.OT_MINE)


    def displayReception(self):
        super(Mercenary, self).displayReception()

        if ret["boom"]:
            self.game.remove_widget(self.mines.pop(str([0, 0])))
