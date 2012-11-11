#!/usr/bin/python
import SocketServer
import sys
from math import sqrt
import logging

import network_protocol as np
from slmap import SLMap

MAP = ""

class Player(object):
    """docstring for Player"""
    def __init__(self, playerType):
        super(Player, self).__init__()
        self.playerType = playerType
        self.pos = None
        self.score = None
        self.mousePos = None
        self.running = True


class GameServerEngine(object):
    """docstring for GameServerEngine"""
    CELL_SIZE = 32
    MIN_NOISE_DIST = 4
    MIN_BEEP_DIST = 4
    MIN_TRAP_DIST = int(1.2 * CELL_SIZE)
    SPY_INITIAL_LIVES = 3
    MERC_INITIAL_LIVES = 1

    (TRAP_FREE, TRAP_MINED, TRAP_DETECTED) = range(0, 3)

    def __init__(self):
        global MAP
        self.logger = logging.getLogger("gs.log")
        super(GameServerEngine, self).__init__()
        self.spy = Player(np.SPY_TYPE)
        self.spy.lives = self.SPY_INITIAL_LIVES
        self.merc = Player(np.MERCENARY_TYPE)
        self.merc.lives = self.MERC_INITIAL_LIVES
        self.mines = []
        self.detectors = []
        self.slm = SLMap(MAP)
        self.walls = self.slm.walls

    def shoot(self, player):
        if player == self.merc:
            #@TODO
            self.spy.lives -= 1
        else:
            self.logger.info("A spy tried to shoot!")

    def drop(self, player, objType):
        print "Drop objType=", objType, "Not yet implemented"# @TODO
        if objType == np.OT_MINE:
            self.mines.append((player.pos.x, player.pos.y))
        elif objType == np.OT_DETECTOR:
            self.detectors.append((player.pos.x, player.pos.y))

    def activate(self, player):
        print "Activate() at pos=", player.pos, "Not yet implemented" # @TODO

    def run(self, player):
        self.logger.info("Run() for player of type", player.playerType)
        player.running = True

    def beep_level(self, p1):
        m = float('inf')
        for mine in self.mines:
            dist = int(abs(p1.pos.x - mine[0])/self.CELL_SIZE + abs(p1.pos.y - mine[1])/self.CELL_SIZE)
            if dist <= self.MIN_BEEP_DIST and dist <= m:
                m = dist
        return m

    def noise_level(self, p1, p2):
        dist = abs(p1.pos.x - p2.pos.x) + abs(p1.pos.y - p2.pos.y)
        if dist < self.MIN_NOISE_DIST:
            return dist

    def trapped(self, player):
        result = False
        i = 0
        l = len(self.mines)
        while i < l:
            m = self.mines[i]
            if sqrt((player.pos.x - m[0])**2 + (player.pos.y - m[1])**2) <= self.MIN_TRAP_DIST:
                del self.mines[i] # This mine just exploded to spy's face, delete it (it multiple mines should explode, they will all blow up)
                result = self.TRAP_MINED
            i += 1
        if result != False:
            player.lives -= 1
            return self.TRAP_MINED
        i = 0
        l = len(self.detectors)
        while i < l:
            m = self.detectors[i]
            if sqrt((player.pos.x - m[0])**2 + (player.pos.y - m[1])**2) <= self.MIN_TRAP_DIST:
                del self.detectors[i]
            i += 1
        
        if result != False:
            return self.TRAP_DETECTED
        else:
            return self.TRAP_FREE



class SLTCPServer(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    __initialized = False

    def __init(self):
        if not self.__initialized:
            self.__initialized = True
            self.logger = logging.getLogger("sltcps.log")
            self.gs = GameServerEngine()

    def handle(self):
        self.__init()
        # self.request is the TCP socket connected to the client
        
        while True:
            rep = ""
            try:
                self.data = np.recv_end(self.request)
                self.logger.info("{} wrote:".format(self.client_address[0]))
                self.logger.info( self.data)
            except Exception as e:
                self.logger.info( "Socket error 2")
                self.logger.info(e)
                break

            lines = [_.strip().split(" ") for _ in self.data.strip().split("\n")]

            self.logger.info( "lines:" + str(lines))

            if lines[0][0] == np.SPY_TXT:
                player = self.gs.spy
                ennemy = self.gs.merc
            else:
                player = self.gs.merc
                ennemy = self.gs.spy

            player.pos = (lines[1][0], lines[1][1])
            player.mousePos = (lines[2][0], lines[2][1])

            TRAPPED = ""
            if player == self.gs.spy:
                trapped = self.gs.trapped(player)
                if trapped != self.gs.TRAP_FREE:
                    TRAPPED = "\n" + np.TRAPPED_TXT + " " + trapped

            l = len(lines)
            i = 3
            while l > i:
                self.logger.info(lines[i][0])
                self.logger.info(np.ACTIVATE_TXT)
                self.logger.info(lines[i][0] == np.ACTIVATE_TXT)

                if lines[i][0] == np.SHOOT_TXT:
                    self.gs.shoot(player)
                elif lines[i][0] == np.OBJECT_TXT:
                    self.gs.drop(player, lines[i][1])
                elif lines[i][0] == np.ACTIVATE_TXT:
                    self.gs.activate(player)
                elif lines[i][0] == np.RUN_TXT:
                    self.gs.run(player)
                i += 1

            try:
                
                if ennemy.pos is not None: # if we've already instantiated the ennemy position
                    rep += str(ennemy.pos.x) + " " + str(ennemy.pos.y)
                    rep += "\n" + np.BEEP_TXT + " " + str(self.gs.beep_level(player, ennemy))
                    rep += "\n" + np.NOISE_TXT + " " + str(self.gs.noise_level(player, ennemy))
                    rep += TRAPPED
                else:
                    rep += "-42 -42"
                self.request.sendall(rep + np.MSG_END)
                self.logger.info("Data sent: " + str(rep))
            except Exception as e:
                self.logger.info("Socket error 3")
                self.logger.info(str(e))
                break
            

if __name__ == "__main__": # for debugging purposes
    if len(sys.argv) > 1:
        MAP = sys.argv[1]
    else:
        print "No map provided"
        sys.exit()

    if len(sys.argv) > 2:
        HOST = sys.argv[2]
    else:
        HOST = "localhost"

    if len(sys.argv) > 3:
        print sys.argv[3]
        PORT = int(sys.argv[3])
    else:
        PORT = None
    if PORT is None or PORT < 0:
        PORT = 9999
    
    print "Connecting to", HOST, PORT
    
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), SLTCPServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()