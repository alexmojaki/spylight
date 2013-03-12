#!/usr/bin/python

import sys

"""
Run the file with the parameter -s to run the server
"""

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        from server.main import runServer
        sys.argv.pop(1)
        runServer()
    else:
        from client.app import SpylightClientApp
        SpylightClientApp().run()
