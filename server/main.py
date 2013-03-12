#!/usr/bin/python
import sys
import logging

from threading import Thread
from ConfigParser import SafeConfigParser

from server.request_handler import TCPRequestHandler

logging.basicConfig(level=logging.DEBUG)

CONFIG_FILE = 'server/spylight.cfg'


def runServer():  # Call it from the root folder
    config = SafeConfigParser()
    config.read(CONFIG_FILE)

    if len(sys.argv) > 1:
        mapname = sys.argv[1]
    else:
        mapname = config.get('GameSetup', "MapPath")

    if len(sys.argv) > 2:
        hostname = sys.argv[2]
    else:
        hostname = config.get('GameSetup', "Hostname")

    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    else:
        port = config.getint('GameSetup', "Port")

    print "Accepting connections to", hostname, port

    server = TCPRequestHandler(config)
    server.gs.setMap(mapname)

    # Create the input thread
    t = Thread(target=handle_input, args=(server,))
    t.daemon = True  # The thread will be killed when the main process stops
    t.start()

    server.run(hostname, port)


def handle_input(server):
    def exit():
        server.stop()
        sys.exit()

    def start():
        print "starting the game (TODO)"
        server.start_game()

    allowed_commands = ["exit", "start"]

    while True:
        command = raw_input("> ")
        if command in allowed_commands:
            locals()[command]()


if __name__ == "__main__":  # for debugging purposes
    # Don't run it from here or enjoy messing with sys.path first
    # Also, change the value of CONFIG_FILE
    runServer()
