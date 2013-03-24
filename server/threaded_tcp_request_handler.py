from SocketServer import StreamRequestHandler


class ThreadedTCPRequestHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        print '{} a écrit :'.format(self.client_address[0])
        print '\t', data.upper()
        self.wfile.write(data.upper)
