#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads
from msgpack import packb as m_pack
from socket import AF_INET, SOCK_STREAM, socket
from struct import pack as s_pack
from sys import argv, exit


if __name__ == '__main__':
    if len(argv) < 3:
        print "usage: dummy_client.py <host> <port>"
        exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((argv[1], int(argv[2])))

    while 1:
        try:
            data = m_pack(loads(raw_input('json > ')))
            data_size = s_pack('!I', len(data))
            s.sendall(data_size + data)
        except Exception as e:
            print e
