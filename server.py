#!/usr/bin/python
import SocketServer
import sys
import network_protocol as np

class Player(object):
    """docstring for Player"""
    def __init__(self, playerType):
        super(Player, self).__init__()
        self.playerType = playerType
        self.pos = None
        self.score = None
        self.mousePos = None


class GameServerEngine(object):
    """docstring for GameServerEngine"""
    def __init__(self):
        super(GameServerEngine, self).__init__()
        self.spy = Player(np.SPY_TYPE)
        self.merc = Player(np.MERCENARY_TYPE)

    def shoot(self, player):
        if player == self.merc:
            print "Not yet implemented" # @TODO
        else:
            print "A spy tried to shoot!"

    def drop(self, player, objType):
        print "Drop objType=", objType, "Not yet implemented"# @TODO

    def activate(self, player):
        print "Activate() at pos=", player.pos, "Not yet implemented"# @TODO
        
        

class SLTCPServer(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def __init(self):
        if not self.__initialized:
            self.__initialized
            self.gs = GameServerEngine()

    def handle(self):
        # self.request is the TCP socket connected to the client
        def recv_end(the_socket):
            End = "\n\n"
            total_data=[]
            data=''
            while True:
                data = the_socket.recv(8192)
                print "DATA:", data
                if End in data:
                    total_data.append(data[:data.find(End)])
                    break
                total_data.append(data)
                if len(total_data) > 1:
                    #check if end_of_data was split
                    last_pair=total_data[-2]+total_data[-1]
                    if End in last_pair:
                        total_data[-2]=last_pair[:last_pair.find(End)]
                        total_data.pop()
                        break
            return ''.join(total_data)
        while True:
            try:
                self.data = recv_end(self.request)
                print "{} wrote:".format(self.client_address[0])
                print self.data
            except Exception as e:
                print "Socket error 2"
                print e
                break

                lines = [_.strip().split(" ") for _ in data.strip().split("\n")]

                if lines[0][0] == np.SPY_TXT:
                    player = self.gs.spy
                else:
                    player = self.gs.merc

                player.pos = (lines[1][0], lines[1][1])
                player.mousePos = (lines[2][0], lines[2][1])

                l = len(lines)
                i = 2
                while l > (i+1):
                    if lines[i][0] == np.SHOOT_TXT:
                        self.gs.shoot(player)
                    elif lines[i][0] == np.OBJECT_TXT:
                        self.gs.drop(player, lines[i][1])
                    elif lines[i][0] == np.ACTIVATE_TXT:
                        self.gs.activate(player)
            try:
                # just send back the same data, but upper-cased
                self.request.sendall(self.data.upper())
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