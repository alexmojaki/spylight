# -*- coding: utf-8 -*-

import sys
import hashlib

import game_constants as const


class SpyLightMap(object):
    """
    Used in server and client. Must stay as plain old python (no kivy here)

    This class uses all coordinates in number of tiles.
    It doesn't know anything about pixels.
    """

    WA_WA0 = 0  # TODO: Rename that constant to something meaningful
    WA_WA1 = 1  # TODO: Rename that constant to something meaningful
    WA_WA2 = 2  # TODO: Rename that constant to something meaningful
    WA_SPY_ONLY_DOOR = 3
    WA_MERC_ONLY_DOOR = 4  # TODO: Rename that constant to something meaningful

    WALL0 = {'section': 'wa', 'value': WA_WA0}
    WALL1 = {'section': 'wa', 'value': WA_WA1}
    WALL2 = {'section': 'wa', 'value': WA_WA2}

    OBSTACLES_TYPES = (WALL0, WALL1, WALL2)  # Wall types that are "obstacles" (static impenetrable rigid bodies)

    SPAWN_MERC = 0
    SPAWN_SPY = 1

    IT_TERMINAL = 0
    IT_BRIEFCASE = 1
    IT_CAMERA = 42
    IT_LAMP = 3

    # Sections: wall, spawn, item, vision
    TERMINAL_KEY = 'T'
    TERMINAL = {'section': 'it', 'value': IT_TERMINAL}
    LAMP_KEY = 'L'
    LAMP = {'section': 'vi', 'value': IT_LAMP}

    PATH_STD = 0

    HFM_TO_MAP = {
        '+': WALL0,
        '-': WALL1,
        '|': WALL2,
        '#': {'section': 'wa', 'value': WA_SPY_ONLY_DOOR},  # Spy-only door
        '@': {'section': 'wa', 'value': WA_MERC_ONLY_DOOR},  # Mercenary-only door
        'M': {'section': 'sp', 'value': SPAWN_MERC},
        'S': {'section': 'sp', 'value': SPAWN_SPY},
        TERMINAL_KEY: TERMINAL,  # Terminal
        'B': {'section': 'it', 'value': IT_BRIEFCASE},  # Briefcase
        'C': {'section': 'vi', 'value': IT_CAMERA},  # Camera
        LAMP_KEY: LAMP,   # Lamp
        ' ': {'section': 'pa', 'value': PATH_STD}
    }

    def __init__(self, filename=None):
        self.title = None
        self.size = (0, 0)
        self.height = 0
        self.width = 0
        self.map_tiles = None  # self.map_tiles[y][x] (1st array is the v-axis)
        self.nb_players = (0, 0)
        self.max_x, self.max_y = 0, 0

        if filename:
            self.load_map(filename)

    def _to_legacy_format(self):
        output = {
            'wa': [],
            'sp': [],
            'it': []
        }
        for y in range(len(self.map_tiles)):
            for x in range(len(self.map_tiles[y])):
                c = self.map_tiles[y][x]
                try:
                    mapc = self.HFM_TO_MAP[c]
                    output[mapc['section']].append(
                        ','.join([str(x), str(y), str(mapc['value'])]))
                except KeyError:
                    pass

        return output

    def load_map(self, filename):
        with open(filename, 'r') as f:
            curMapLine = -1
            for line in f:
                if line == "" or line[0] == '#':  # Empty line or comment
                    continue
                elif line.find('size:') == 0:  # Line starts with size
                    strsize = line.split(':')[1].split()
                    self.size = (int(strsize[0]), int(strsize[1]))
                    self.width, self.height = self.size
                    self.map_tiles = [None] * self.height
                    curMapLine = self.height - 1
                elif line.find('title:') == 0:  # Line starts with size
                    self.title = line.split(':')[1].replace('\n', '')
                elif line.find('players:') == 0:  # Line starts with players
                    strnbp = line.split(':')[1].split()
                    self.nb_players = (int(strnbp[0]), int(strnbp[1]))
                else:  # Regular map line
                    if self.map_tiles is None:
                        print "La taille de la carte doit être déclarée avant de la dessiner."
                        sys.exit()
                    else:
                        mapLine = []
                        for c in line:
                            mapLine.append(c)
                        try:
                            self.map_tiles[curMapLine] = mapLine
                        except IndexError:
                            print 'Erreur de taille de la carte.'
                            sys.exit()
                        curMapLine = curMapLine - 1
            self.max_x, self.max_y = self.width * const.CELL_SIZE - 1, self.height * const.CELL_SIZE - 1

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
        """
        Warning: this class only uses tile numbers, so x and y are the
        coordinates of the tile in the tile matrix.
        """
        try:
            c = self.map_tiles[y][x]
            ctype = self.HFM_TO_MAP[c]
            if ctype['section'] == 'wa':
                return ctype['value']
            else:
                return -1
        except KeyError:
            return -1

    def getItem(self, x, y):
        """
        Warning: this class only uses tile numbers, so x and y are the
        coordinates of the tile in the tile matrix.
        """
        try:
            c = self.map_tiles[y][x]
            ctype = self.HFM_TO_MAP[c]
            if ctype['section'] == 'it':
                return ctype['value']
            else:
                return -1
        except KeyError:
            return -1

    def get_hash(self):
        m = hashlib.sha1()
        m.update(str(self.map_tiles))
        return m.hexdigest()

    # @function is_obstacle : Tells if the given coordinates belongs to a map obstacle (something that cannot be gone
    # through, a static rigid body)
    # @param{integer} x : x coordinate (game's coordinate)
    # @param{integer} y : y coordinate (game's coordinate)
    # @return{bool} True if yes, False if no
    def is_obstacle(self, x, y):
        row = y // const.CELL_SIZE
        col = x // const.CELL_SIZE
        return self.is_obstacle_from_cell_coords(row, col)

    # @function is_obstacle : Tells if the given coordinates belongs to a map obstacle (something that cannot be gone
    # through, a static rigid body)
    # @param{integer} row : map_tiles matrix row
    # @param{integer} col : map_tiles matrix column
    # @return{bool} True if yes, False if no
    def is_obstacle_from_cell_coords(self, row, col):
        if row >= self.height or row < 0 or col < 0 or col >= self.width:
            return False
        try:
            cell = self.HFM_TO_MAP[self.map_tiles[row][col]]
            if cell in self.OBSTACLES_TYPES:
                return True
            return False
        except KeyError:
            return False

    def get_cameras(self):
        cameras = []
        for y in xrange(self.size[1]):
            for x in xrange(self.size[0]):
                if self.map_tiles[y][x] == 'C':
                    print x, y
                    cameras.append((x, y))
        return cameras

    def get_tile(self, x, y):
        '''
        Returns the section and the value of a tile.
        If it's empty, (None, None) is returned
        '''
        try:
            tmp = self.HFM_TO_MAP[self.map_tiles[y][x]]
            return (tmp['section'], tmp['value'])
        except KeyError:
            return (None, None)


if __name__ == '__main__':
    slm = SpyLightMap(sys.argv[1])
    # slm.print_legacy_map()
    print slm.get_cameras()
