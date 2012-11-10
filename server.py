#!/usr/bin/python
import SocketServer
import sys
import network_protocol as np
from math import sqrt

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

    (OT_MINE, OT_MIRROR) = range(0, 2)

    def __init__(self):
        super(GameServerEngine, self).__init__()
        self.spy = Player(np.SPY_TYPE)
        self.merc = Player(np.MERCENARY_TYPE)
        self.mines = []

    def shoot(self, player):
        if player == self.merc:
            print "Not yet implemented" # @TODO
        else:
            print "A spy tried to shoot!"

    def drop(self, player, objType):
        print "Drop objType=", objType, "Not yet implemented"# @TODO
        if objType == self.OT_MINE:
            self.mines.append((player.x, player.y))

    def activate(self, player):
        print "Activate() at pos=", player.pos, "Not yet implemented" # @TODO

    def run(self, player):
        print "Run() for player of type", player.playerType
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
        for m in mines:
            if sqrt((player.pos.x - m[0])**2 + (player.pos.y - m[1])) <= self.MIN_TRAP_DIST:
                pass

        
        

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
            self.gs = GameServerEngine()

    def handle(self):
        self.__init()
        # self.request is the TCP socket connected to the client
        
        while True:
            try:
                self.data = np.recv_end(self.request)
                print "{} wrote:".format(self.client_address[0])
                print self.data
            except Exception as e:
                print "Socket error 2"
                print e
                break

            lines = [_.strip().split(" ") for _ in self.data.strip().split("\n")]

            print "lines:", lines

            if lines[0][0] == np.SPY_TXT:
                player = self.gs.spy
                ennemy = self.gs.merc
            else:
                player = self.gs.merc
                ennemy = self.gs.spy

            player.pos = (lines[1][0], lines[1][1])
            player.mousePos = (lines[2][0], lines[2][1])

            l = len(lines)
            i = 3
            while l > i:
                print lines[i][0]
                print np.ACTIVATE_TXT
                print lines[i][0] == np.ACTIVATE_TXT

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
                rep = str(ennemy.pos.x) + " " + str(ennemy.pos.y)
                rep += "\n" + np.BEEP_TXT + " " + str(self.gs.beep_level(player, ennemy))
                rep += "\n" + np.NOISE_TXT

                self.request.sendall(rep)
            except:
                print "Socket error 3"
                break
            

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print sys.argv[1]
        PORT = int(sys.argv[1])
    else:
        PORT = None
    if PORT is None or PORT < 0:
        PORT = 9999
    
    HOST = "localhost"

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), SLTCPServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()