#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.spylight_server import SpylightServer


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print 'usage: {} host port'.format(sys.argv[0])
        sys.exit(1)

    SpylightServer(sys.argv[1], int(sys.argv[2]), '').start()
