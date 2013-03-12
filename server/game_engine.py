import common.game_constants as c
from math import sqrt
from common.slmap import SLMap
import common.network_protocol as np
import logging


class GameServerEngine(object):
    """docstring for GameServerEngine"""
    MIN_NOISE_DIST = 4  # in cells
    MIN_BEEP_DIST = 4  # in cells
    MIN_TRAP_DIST = int(1.2 * c.CELL_SIZE)
    SPY_INITIAL_LIVES = 3
    MERC_INITIAL_LIVES = 1
    CAP_TIME = 4  # seconds
    TIME_FREQ = 60  # 60 ticks by second

    (TRAP_FREE, TRAP_MINED, TRAP_DETECTED) = range(0, 3)

    def __init__(self, config):
        self.config = config

    def setUp(self, playersIdMsg):
        self.spy = Player(np.SPY_TYPE)
        self.spy.lives = self.SPY_INITIAL_LIVES
        self.merc = Player(np.MERCENARY_TYPE)
        self.merc.lives = self.MERC_INITIAL_LIVES
        self.mines = []
        self.detectors = []

    def setMap(self, mapPath):
        self.slm = SLMap(mapPath)
        self.walls = self.slm.walls

    def shoot(self, player):
        if player == self.merc:
            self.spy.lives -= 1
        else:
            logging.info("A spy tried to shoot!")

    def drop(self, player, objType):
        print "Drop objType=", objType
        if objType == np.OT_MINE:
            print "Obj is a mine"
            self.mines.append((player.pos[0], player.pos[1]))
        elif objType == np.OT_DETECTOR:
            self.detectors.append((player.pos[0], player.pos[1]))
        logging.info(self.mines)

    def activate(self, player):
        print "Activate() at pos=" + str(player.pos) + "Not yet implemented"  # @TODO
        x = player.pos[0] / self.c.CELL_SIZE
        y = player.pos[1] / self.c.CELL_SIZE
        if not player.capping:
            player.cap = 0
        if self.slm.getItem(x, y) == 0:
            player.cap += 1

    def run(self, player):
        logging.info("Run() for player of type" + str(player.team))
        player.running = True

    def beep_level(self, p1):
        m = 0
        for mine in self.mines:
            dist = int(abs(p1.pos[0] - mine[0])/self.c.CELL_SIZE + abs(p1.pos[1] - mine[1])/self.c.CELL_SIZE)
            if dist <= self.MIN_BEEP_DIST:
                level = int(self.MIN_BEEP_DIST - (dist/self.c.CELL_SIZE))
                if level > m:
                    m = level
        return m

    def noise_level(self, p1, p2):
        dist = abs(p1.pos[0] - p2.pos[0]) + abs(p1.pos[1] - p2.pos[1])
        if dist <= self.MIN_NOISE_DIST:
            return int(self.MIN_NOISE_DIST - (dist/self.c.CELL_SIZE))
        else:
            return 0

    def trapped(self, player):
        result = False
        i = 0
        l = len(self.mines)
        while i < l:
            m = self.mines[i]
            if sqrt((player.pos[0] - m[0])**2 + (player.pos[1] - m[1])**2) <= self.MIN_TRAP_DIST:
                del self.mines[i]  # This mine just exploded to spy's face, delete it (it multiple mines should explode, they will all blow up)
                result = self.TRAP_MINED
            i += 1
        if not result:
            player.lives -= 1
            return self.TRAP_MINED
        i = 0
        l = len(self.detectors)
        while i < l:
            m = self.detectors[i]
            if sqrt((player.pos[0] - m[0])**2 + (player.pos[1] - m[1])**2) <= self.MIN_TRAP_DIST:
                del self.detectors[i]
            i += 1

        if not result:
            return self.TRAP_DETECTED
        else:
            return self.TRAP_FREE

    def exit(self):
        print "Exiting the game. (TODO)"


class Player(object):
    """docstring for Player"""
    def __init__(self, team):
        super(Player, self).__init__()
        self.id = id
        self.team = team
        self.pos = None
        self.score = None
        self.aimAngle = None
        self.running = True
        self.capping = False
