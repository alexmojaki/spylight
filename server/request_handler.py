import socket
import logging
import sys

import common.network_protocol as np
from server.game_engine import GameServerEngine


class TCPRequestHandler(object):

    def __init__(self, config):
        self.gs = GameServerEngine(config)
        self.config = config

    def run(self, hostname, port):
        maxPlayers = self.config.getint("GameSetup", "MaxTeamSize") * 2

        self.hostname = hostname
        self.port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.bind((hostname, port))
        self._s.listen(maxPlayers)  # at max 2 connections
        self.playerSockets = []  # Client socket for each player
        self.playerIdMsgs = []  # Identification messages recieved when the player connects.

        # Waiting for the connections
        while self._s is not None and len(self.playerSockets) < maxPlayers:
            self.register_client(self._s.accept())

        # All players are connected. The socket is then closed.
        if self._s:
            self._s.close()
            self._s = None

        logging.debug("Starting game setup")

        if self.playerSockets:
            # Initializing the game
            self.gs.setUp(self.playerIdMsgs)  # @TODO: game setup
        else:
            logging.warning("No client registered for this game session.")
            sys.exit()

        logging.debug("Finished the game setup")
        while True:
            for request in self.playerSockets:
                rep = ""
                try:
                    self.data = np.recv_end(request)
                    logging.info(self.data)
                except socket.error, e:
                    logging.debug(str(e))
                    break

                lines = [_.strip().split(" ") for _ in self.data.strip().split("\n")]

                logging.info("lines:" + str(lines))

                if lines[0][0] == np.SPY_TXT:
                    player = self.gs.spy
                    ennemy = self.gs.merc
                else:
                    print "@TODO: REMAKE PROTOCOL"
                    player = self.gs.merc
                    ennemy = self.gs.spy

                player.pos = (int(lines[1][0]), int(lines[1][1]))
                player.mousePos = (int(lines[2][0]), int(lines[2][1]))

                TRAPPED = ""
                DEAD = False
                if player == self.gs.spy:
                    trapped = self.gs.trapped(player)
                    if trapped != self.gs.TRAP_FREE:
                        TRAPPED = "\n" + np.TRAPPED_TXT + " " + str(trapped)
                        if trapped == self.gs.TRAP_MINED:
                            DEAD = True

                l = len(lines)
                i = 3
                while l > i:
                    logging.info(lines[i][0])
                    logging.info(np.ACTIVATE_TXT)
                    logging.info(lines[i][0] == np.ACTIVATE_TXT)

                    if lines[i][0] == np.SHOOT_TXT:
                        self.gs.shoot(player)
                    elif lines[i][0] == np.OBJECT_TXT:
                        self.gs.drop(player, int(lines[i][1]))
                    elif lines[i][0] == np.ACTIVATE_TXT:
                        self.gs.activate(player)
                    elif lines[i][0] == np.RUN_TXT:
                        self.gs.run(player)
                    else:
                        player.capping = False  # the player is not doing any of the previous ones, so it is obviously not capping (even in the following lines). THIS CONDITION HAS TO BE KEPT INE THE "ELSE" /!\
                    i += 1

                try:
                    if ennemy.pos is not None:  # if we've already instantiated the ennemy position
                        rep += str(ennemy.pos[0]) + " " + str(ennemy.pos[1])
                        rep += "\n" + np.BEEP_TXT + " " + str(self.gs.beep_level(player))
                        rep += "\n" + np.NOISE_TXT + " " + str(self.gs.noise_level(player, ennemy))
                    else:
                        rep += "-42 -42"
                    rep += TRAPPED
                    if DEAD:
                        rep += "\n" + np.DEAD_TXT
                    if player.capping:
                        rep += "\n" + np.CAPTURE_TXT + " " + int(player.cap * 100 / (self.gs.TIME_FREQ * self.gs.CAP_TIME))

                    request.sendall(rep + np.MSG_END)
                    logging.info("Data sent: " + str(rep))
                except Exception as e:
                    logging.info("Socket error 3")
                    logging.info(str(e))
                    break

                if request == self._s1:
                    request = self._s2
                else:
                    request = self._s1
        logging.info('Conection closed')
        self._s1.close()
        self._s2.close()

    def register_client(self, (clientSocket, address)):
        clientIdMsg = np.recv_end(clientSocket)
        if clientIdMsg == "stop_accept":
            self._s.close()
            self._s = None
            logging.info("Recieved the start message.")
        else:
            self.playerSockets.append(clientSocket)
            self.playerIdMsgs.append(clientIdMsg)  # TODO: verifying and identifying the players
            logging.debug("connection recieved ({0}/{1})".format(
                len(self.playerSockets), self.config.getint("GameSetup", "MaxTeamSize") * 2))

        pass

    def start_game(self):
        """ Connects to the listening socket and sends a message to close it. """
        if self._s is not None:
            tmpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmpsocket.connect((self.hostname, self.port))
            tmpsocket.sendall("stop_accept")
            tmpsocket.close()
        else:
            logging.warning("The game game should be started already.")

    def stop(self):
        self.gs.exit()
