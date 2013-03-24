from SocketServer import ThreadingMixIn, TCPServer


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass
