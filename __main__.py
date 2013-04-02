#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server.spylight_server import SpylightServer


if __name__ == '__main__':
    if not len(sys.argv) == 4 or sys.argv[1] != '-s':
        print 'usage: {} -s host port'.format(sys.argv[0])
        sys.exit(1)

    SpylightServer(sys.argv[2], int(sys.argv[3]), '').start()
