# -*- coding: utf-8 -*-

import sys
import hashlib
import math
import ast

import game_constants as const


class SpyLightMap(object):
    """
    Used in server and client. Must stay as plain old python (no kivy here)

    This class uses all coordinates in number of tiles.
    It doesn't know anything about pixels.
    """

    WA_WA0 = 1  # TODO: Rename that constant to something meaningful
    WA_WA1 = 2  # TODO: Rename that constant to something meaningful
    WA_WA2 = 3  # TODO: Rename that constant to something meaningful
    WA_SPY_ONLY_DOOR = 4
    WA_MERC_ONLY_DOOR = 5  # TODO: Rename that constant to something meaningful

    WALL0 = {'section': 'wa', 'value': WA_WA0}
    WALL1 = {'section': 'wa', 'value': WA_WA1}
    WALL2 = {'section': 'wa', 'value': WA_WA2}

    OBSTACLES_TYPES = (WALL0, WALL1, WALL2)  # Wall types that are "obstacles" (static impenetrable rigid bodies)

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
        'M': {'section': 'sp', 'value': const.MERC_TEAM},
        'S': {'section': 'sp', 'value': const.SPY_TEAM},
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
        self.witdh = 0
        self.map_tiles = None  # self.map_tiles[col][row]
        self.nb_players = [0, 0]  # nb players in team 0, nb players in team 1
        self.extra_info = {}  # Contains misc. info regarding specific tiles
                              # keys: '{0}-{1}'.format(row, col)
        self.spawns = [[], []]  # spawn points for both teams. The spawn a
                                # particular player is
                                # self.spawns[team_id][player_id]
                                # (see get_spawn_point(team_id, player_id))
                                # the lowest id will spawn at the most top left
                                # position
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
        file_str = ''
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
                elif line.find('info:') == 0:  # Line starts with info
                    self._parse_info_line(line.split(':')[1].replace('\n', ''))
                else:  # Regular map line
                    if self.map_tiles is None:
                        print "La taille de la carte doit être déclarée avant de la dessiner."
                        sys.exit()
                    else:
                        self._parse_map_line(line, curMapLine)
                        curMapLine = curMapLine - 1
                file_str += line
        self.max_x = self.width * const.CELL_SIZE - 1
        self.max_y = self.height * const.CELL_SIZE - 1

#        print 'spawns:', self.spawns

        # File hash
        m = hashlib.sha1()
        m.update(str(file_str))
        self.hash = m.hexdigest()

    def _parse_map_line(self, line, curMapLine):
        mapLine = []
        for c in line:
            mapLine.append(c)

            if c in 'SM':  # it's a spawn point
                team = self.HFM_TO_MAP[c]['value']
                self.spawns[team].append([len(mapLine)-1, curMapLine])

        try:
            self.map_tiles[curMapLine] = mapLine
        except IndexError:
            print 'Erreur de taille de la carte.'
            sys.exit()

    def _parse_info_line(self, line):
        fields = line.split(',')
        object_key = '{0}-{1}'.format(fields[0], fields[1])
        object_info = {}
        for field in fields[3:]:
            key, value = field.split('=')
            object_info[key] = ast.literal_eval(value)
        try:
            self.extra_info[object_key] = object_info
        except KeyError:
            print 'Erreur de lecture de la carte: ', line
            sys.exit()

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

    def getWallType(self, row, col):
        """
        Warning: this class only uses tile numbers, so row and col are the
        coordinates of the tile in the tile matrix.
        """
        try:
            c = self.map_tiles[col][row]
            ctype = self.HFM_TO_MAP[c]
            if ctype['section'] == 'wa':
                return ctype['value']
            else:
                return None
        except KeyError:
            return None

    def getItem(self, row, col):
        """
        Warning: this class only uses tile numbers, so row and col are the
        coordinates of the tile in the tile matrix.
        """
        try:
            c = self.map_tiles[col][row]
            ctype = self.HFM_TO_MAP[c]
            if ctype['section'] == 'it':
                return ctype['value']
            else:
                return None
        except KeyError:
            return None

    def get_hash(self):
        return self.hash

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

    def get_camera_orientation(self, row, col):
        '''
        Takes the position of a camera, returns its orientation
        '''
        try:
            return self.extra_info['{0}-{1}'.format(row, col)]['orientation']
        except KeyError:
            print 'No camera info registered for coordinates', row, col
            return 0

    def get_cameras(self):
        cameras = []
        for col in xrange(self.size[1]):
            for row in xrange(self.size[0]):
                if self.map_tiles[col][row] == 'C':
                    print row, col
                    cameras.append((row, col))
        return cameras

    def get_tile(self, row, col):
        '''
        Returns the section and the value of a tile.p
        If it's empty, (None, None) is returned
        '''
        try:
            tmp = self.HFM_TO_MAP[self.map_tiles[col][row]]
            return (tmp['section'], tmp['value'])
        except KeyError:
            return (None, None)

    def get_spawn_point(self, teamid, playerid):
        '''
        Returns the spawn tile (row,col) for a player
        '''
        # number of players in the other teams
        offset = sum(self.nb_players[:teamid])
        try:
            if offset <= playerid:
                return self.spawns[teamid][playerid - offset]
            print 'Wrong player ({}) or team ({}) id'.format(playerid, teamid)
        except IndexError:
            msg = 'Error retrieving the spawn point     for player {} in team {}'
            print msg.format(playerid, teamid)


if __name__ == '__main__':
    slm = SpyLightMap(sys.argv[1])
    # slm.print_legacy_map()
    print slm.get_spawn_point(input('team:'), input('player:'))
    # print slm.get_cameras()
