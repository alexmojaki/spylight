#!/usr/bin/python
import socket
import sys
from time import sleep
import logging

import network_protocol as np

class ClientNetworker(object):
    """docstring for ClientNetworker"""

    def __init__(self, playerType):
        super(ClientNetworker, self).__init__()
        self.logger = logging.getLogger("cn.log")
        self.logger.addHandler(logging.FileHandler("cn.log"))
        self.logger.setLevel(logging.INFO)
        if playerType == np.SPY_TYPE:
            self.__player_data = np.SPY_TXT
        elif playerType == np.MERCENARY_TYPE:
            self.__player_data = np.MERCERNARY_TXT
        self.__reset_data()

    def drop(self, obj_id):
        self.__drop_data = "\n" + np.OBJECT_TXT + " " + str(obj_id)

    def shoot(self):
        self.__shoot_data = "\n" + np.SHOOT_TXT

    def activate(self):
        self.__activate_data = "\n" + np.ACTIVATE_TXT

    def pos(self, x, y):
        self.__pos_data = "\n" + str(x) + " " + str(y)

    def run(self):
        self.__run_data = "\n" + np.RUN_TXT

    def mouse_pos(self, x, y):
        self.__mouse_pos_data = "\n" + str(x) + " " + str(y)

    def connect(self, host, port):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((host, port))

    def send(self):
        tosend = self.__player_data + self.__pos_data + self.__mouse_pos_data + self.__run_data + self.__shoot_data + self.__activate_data + self.__drop_data + np.MSG_END
        
        self.logger.info("Sending:" + str(tosend))

        self.__s.sendall(tosend)
        # Clear the values of the data so that we don't resend them at next round
        # We don't do it for __pos_data as, at worst, the player will keep its mouse position
        self.__reset_data()

    def __reset_data(self):
        self.__shoot_data = ""
        self.__activate_data = ""
        self.__drop_data = ""
        self.__mouse_pos_data = ""
        self.__run_data = ""

    def recv(self):
        res = {}
        res["noise"] = 0
        res["beep"] = 0
        res["trapped"] = -1
        res["dead"] = False
        res["lost"] = False

        data = np.recv_end(self.__s).strip()
        if data == "":
            return res
        lines = [_.split(" ") for _ in data.split("\n")]

        res["ennemy"] = (int(lines[0][0]), int(lines[0][1]))
        l = len(lines)
        i = 1

        while l > i:
            if lines[i][0] == np.NOISE_TXT:
                res["noise"] = int(lines[i][1])
            elif lines[i][0] == np.BEEP_TXT:
                res["beep"] = int(lines[i][1])
            elif lines[i][0] == np.TRAPPED_TXT:
                res["trapped"] = int(lines[i][1])
            elif lines[i][0] == np.DEAD_TXT:
                res["dead"] = True
            elif lines[i][0] == np.DEAD_TXT:
                res["lost"] = True
            i += 1

        return res



if __name__ == '__main__': # debugging purposes
    cn = ClientNetworker(int(sys.argv[1]))
    cn.connect("localhost", 9999)
    x, y = 0, 0
    while True:
        sleep(0.1)
        x += 1
        y += 2
        cn.pos(x, y)
        cn.mouse_pos(0, 0)
        cn.activate()
        cn.send()
        print "Data sent. Recving..."
        print cn.recv()
