import sys


class SpyLightMap(object):
    """
    Used in server and client. Must stay as plain old python (no kivy here)
    """

    HFM_TO_MAP = {
        '+': {'section': 'wa', 'value': '0'},
        '-': {'section': 'wa', 'value': '1'},
        '|': {'section': 'wa', 'value': '2'},
        '#': {'section': 'wa', 'value': '0'},  # Spy-only door
        '@': {'section': 'wa', 'value': '0'},  # Mercenary-only door
        'M': {'section': 'sp', 'value': '0'},
        'S': {'section': 'sp', 'value': '1'},
        'T': {'section': 'it', 'value': '0'},  # Terminal
        'B': {'section': 'it', 'value': '1'},  # Briefcase
        'C': {'section': 'it', 'value': '2'},  # Camera
        'L': {'section': 'it', 'value': '3'}   # Lamp
    }

    def __init__(self):
        self.title = None
        self.size = (0, 0)
        self.height = 0
        self.witdh = 0
        self.map_tiles = []
        self.nb_players = (0, 0)

    def _to_legacy_format(self):
        output = {
            'wa': [],
            'sp': [],
            'it': []
        }
        for y in range(len(self.map_tiles)):
            for x in range(len(self.map_tiles[y])):
                c = self.map_tiles[y][x]
                if c in self.HFM_TO_MAP:
                    mapc = self.HFM_TO_MAP[c]
                    output[mapc['section']].append(
                        ','.join([str(x), str(y), mapc['value']]))

        return output

    def load_map(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                if line == "" or line[0] == '#':  # Empty line or comment
                    continue
                elif line.find('size:') == 0:  # Line starts with size
                    strsize = line.split(':')[1].split()
                    self.width, self.height = self.size = (int(strsize[0]), int(strsize[1]))
                elif line.find('title:') == 0:  # Line starts with size
                    self.title = line.split(':')[1].replace('\n', '')
                elif line.find('players:') == 0:  # Line starts with players
                    strnbp = line.split(':')[1].split()
                    self.nb_players = (int(strnbp[0]), int(strnbp[1]))
                else:  # Regular map line
                    mapLine = []
                    for c in line:
                        mapLine.append(c)
                    self.map_tiles.append(mapLine)

    def print_legacy_map(self):
        output = self._to_legacy_format()
        print "SLMap 1"
        print self.title
        print self.size[0], self.size[1]
        print 'sp:'
        print '\n'.join(''.join(l) for l in output['sp'])
        print 'wa:'
        print '\n'.join(''.join(l) for l in output['wa'])
        print 'it:'
        print '\n'.join(''.join(l) for l in output['it'])
        # print nb_players

    def getWallType(self, x, y):
        c = self.map_tiles[y][x]
        if c in self.HFM_TO_MAP and self.HFM_TO_MAP[c]['section'] == 'wa':
            return self.HFM_TO_MAP[c]['value']
        else:
            return -1

    def getItem(self, x, y):
        c = self.map_tiles[y][x]
        if c in self.HFM_TO_MAP and self.HFM_TO_MAP[c]['section'] == 'it':
            return self.HFM_TO_MAP[c]['value']
        else:
            return -1


if __name__ == '__main__':
    slm = SpyLightMap().load_map(sys.argv[1])
    slm.print_legacy_map()
