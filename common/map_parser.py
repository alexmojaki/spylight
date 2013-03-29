import sys
import game_constants as const


class SpyLightMap(object):
    """
    Used in server and client. Must stay as plain old python (no kivy here)
    """

    WA_WA0 = 0 # TODO: Rename that constant to something meaningful
    WA_WA1 = 1 # TODO: Rename that constant to something meaningful
    WA_WA2 = 2 # TODO: Rename that constant to something meaningful
    WA_SPY_ONLY_DOOR = 3
    WA_MERC_ONLY_DOOR = 4 # TODO: Rename that constant to something meaningful

    OBSTACLES_TYPES = (WA_WA0, WA_WA1, WA_WA2) # Wall types that are "obstacles" (static impenetrable rigid bodies)
 
    SP_SP0 = 0 # TODO: Rename that constant to something meaningful
    SP_SP1 = 1 # TODO: Rename that constant to something meaningful

    IT_TERMINAL = 0
    IT_BRIEFCASE = 1
    IT_CAMERA = 2
    IT_LAMP = 3

    HFM_TO_MAP = {
        '+': {'section': 'wa', 'value': SpyLightMap.WA_WA0 },
        '-': {'section': 'wa', 'value': SpyLightMap.WA_WA1 },
        '|': {'section': 'wa', 'value': SpyLightMap.WA_WA2 },
        '#': {'section': 'wa', 'value': SpyLightMap.WA_SPY_ONLY_DOOR },  # Spy-only door
        '@': {'section': 'wa', 'value': SpyLightMap.WA_MERC_ONLY_DOOR },  # Mercenary-only door
        'M': {'section': 'sp', 'value': SpyLightMap.SP_SP0 },
        'S': {'section': 'sp', 'value': SpyLightMap.SP_SP1 },
        'T': {'section': 'it', 'value': SpyLightMap.IT_TERMINAL },  # Terminal
        'B': {'section': 'it', 'value': SpyLightMap.IT_BRIEFCASE },  # Briefcase
        'C': {'section': 'it', 'value': SpyLightMap.IT_CAMERA },  # Camera
        'L': {'section': 'it', 'value': SpyLightMap.IT_LAMP}   # Lamp
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

    # @function is_obstacle : Tells if the given coordinates belongs to a map obstacle (something that cannot be gone through, a static rigid body)
    # @param{integer} x : x coordinate (game's coordinate)
    # @param{integer} y : y coordinate (game's coordinate)
    # @return{bool} True if yes, False if no
    def is_obstacle(self, x, y):
        row = y // const.CELL_SIZE
        col = x // const.CELL_SIZE
        if row > self.height or row < 0 or col < 0 or col > self.width:
            return False
        if self.HFM_TO_MAP[self.map_tiles[row][col]] in self.OBSTACLES_TYPES:
            return True
        return False


if __name__ == '__main__':
    slm = SpyLightMap().load_map(sys.argv[1])
    slm.print_legacy_map()
