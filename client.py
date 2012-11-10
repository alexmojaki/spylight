#!/usr/bin/python
import socket
import sys
import network_protocol as np
from time import sleep

class ClientNetworker(object):
    """docstring for ClientNetworker"""

    def __init__(self, playerType):
        super(ClientNetworker, self).__init__()
        if playerType == np.SPY_TYPE:
            self.__player_data = np.SPY_TXT
        elif playerType == np.MERCENARY_TYPE:
            self.__player_data = np.MERCERNARY_TXT
        self.__reset_data()

    def drop(self, id):
        self.__drop_data = np.OBJECT_TXT + str(id)

    def shoot(self):
        self.__shoot_data = np.SHOOT_TXT

    def activate(self):
        self.__activate_data = np.ACTIVATE_TXT

    def pos(self, x, y):
        self.pos_data = "\n" + str(x) + " " + str(y)

    def connect(self, host, port):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((host, port))

    def send(self):
        tosend = self.__player_data + self.pos_data + self.__shoot_data + self.__activate_data + self.__drop_data + np.MSG_END
        print "Sending:", tosend
        self.__s.sendall(tosend)
        # Clear the values of the data so that we don't resend them at next round
        # We don't do it for pos_data as, at worst, the player will keep its mouse position
        self.__reset_data()

    def __reset_data(self):
        self.__shoot_data = ""
        self.__activate_data = ""
        self.__drop_data = ""


if __name__ == '__main__':
    cn = ClientNetworker(np.SPY_TYPE)
    cn.connect("localhost", 9999)
    x, y =0,0
    while True:
        sleep(1)
        x += 1
        y += 2
        cn.pos(x, y)
        cn.activate()
        cn.send()
