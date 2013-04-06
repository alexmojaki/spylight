#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# To test the client:
# 1. Start the mock server: `python client/mock_server.py`
# 2. Start the client: `python __main__.py`
# Together in one line:  `python client/mock_server.py&; python __main__.py`

if __name__ == '__main__':
    if len(sys.argv) == 1:
        from client.app import SpylightClientApp
        SpylightClientApp().run()
    elif len(sys.argv) == 2 and sys.argv[1] == '-s':
        from server.spylight_server import SpylightServer
        SpylightServer().start()
    else:
        print 'usage: spylight [-s]'
        sys.exit(1)
