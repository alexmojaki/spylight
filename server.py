#!/usr/bin/python
import SocketServer
import sys

class GameServerEngine(object):
    """docstring for GameServerEngine"""
    def __init__(self):
        super(GameServerEngine, self).__init__()
        
        
        

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        def recv_end(the_socket):
            End = "\n\n"
            total_data=[]
            data=''
            while True:
            data=the_socket.recv(8192)
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
            return ''.join(total_data)
        while True:
            try:
                self.data = recv_end(self.request)
                print "{} wrote:".format(self.client_address[0])
                print self.data
                # just send back the same data, but upper-cased
                self.request.sendall(self.data.upper())
            except:
                break

if __name__ == "__main__":
    if sys.argv[0] is not None:
        PORT = int(sys.argv[0])
    if PORT is None or PORT < 0:
        PORT = 9999
    
    HOST = "localhost"

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()