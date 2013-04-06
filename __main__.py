#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# To test the client:
# 1. Start the mock server: `python client/mock_server.py`
# 2. Start the client: `python __main__.py`
# Together in one line:  `python client/mock_server.py&; python __main__.py`
#

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] != '-s':
        if not len(sys.argv) == 4:
            print 'usage: {} -s host port'.format(sys.argv[0])
            sys.exit(1)
        else:
            from server.spylight_server import SpylightServer
            SpylightServer(sys.argv[2], int(sys.argv[3]), '').start()

    else:
        from client.app import SpylightClientApp
        SpylightClientApp().run()
