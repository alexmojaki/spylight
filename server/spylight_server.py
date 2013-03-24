from threaded_tcp_server import ThreadedTCPServer
from game_engine import GameEngine


class SpylightServer:
    def __init__(self, host, port, map_file, config_file='config.ini'):
        self.init_game_engine(config_file, map_file)
        self.start_server(host, port, self._game_engine.get_nb_players())

    def init_game_engine(self, config_file, map_file):
        self._game_engine = GameEngine(config_file, map_file)

    def start_server(self, host, port, player_number):
        print host
        self._tcp_server = ThreadedTCPServer(host, port, player_number)
        self._tcp_server_thread = self._tcp_server.threaded_serve_forever()

if __name__ == '__main__':
    SpylightServer('0.0.0.0', 12321, '')
