from threading import Thread
from SocketServer import ThreadingMixIn, TCPServer

from threaded_tcp_request_handler import ThreadedTCPRequestHandler


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, host, port, client_number):
        self._client_number = client_number
        print host
        super(ThreadedTCPServer, self).__init__((host, port),
                                                ThreadedTCPRequestHandler)

    def threaded_serve_forever(self, daemon=True):
        thread = Thread(target=self.serve_forever)
        thread.daemon = daemon
        thread.start()
        return thread
