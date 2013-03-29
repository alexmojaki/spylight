#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event

from config_handler import ConfigHandler
from config_helper import default_config, option_types
from common.map_parser import SpyLightMap

import common.game_constants as const
import common.utils as utils

class Player(object):
    """Player class, mainly POCO object"""
    PLAYER_RADIUS = 5
    def __init__(self, player_id):
        super(Player, self).__init__()
        self.player_id = player_id
        self.posx = 0 
        self.posy = 0 

class Weapon(object):
    """Weapong class, mainly a POCO object"""
    def __init__(self, _range, angle_error):
        super(Weapon, self).__init__()
        self.range = _range
        self.angle_error = angle_error
        

class GameEngine(object):
    _instances = {}
    players = None

    def __new__(cls, *args, **kargs):
        if GameEngine._instances.get(cls) is None:
            GameEngine._instances[cls] = object.__new__(cls, *args, **kargs)
        return GameEngine._instances[cls]

    def init(self, config_file, map_file):
        self._loop = Event()

        self.load_config(config_file)
        self.load_map(map_file)

    @property
    def loop(self):
        return not self._loop.is_set()

    def load_config(self, config_file):
        self.config = ConfigHandler(config_file, default_config, option_types)

    def load_map(self, map_file):
        self.slmap = SpyLightMap()
        self.slmap.load_map(map_file)
        self._player_number = 4  # TODO: Update with the true player number
                                 #       read from the map file.
        # Loading players
        self._players = [Player(i) for i in xrange(0, self._player_number)]
        # Do some things like settings the weapon for each player...

    def get_nb_players(self):
        return self._player_number

    def start(self):
        self._loop.clear()

    def updateMovementDir(self, pid, angle):
        self._players[pid].movAngle = angle

    # @param pid player id
    # @param angle shoot angle, kivy convention, in degree
    def shoot(self, pid, angle):
        # Direction of the bullet (normalized vector)
        a = radians(angle)
        normalized_direction_vector = (-sin(a), cos(a)) # x, y, but in the kivy convention
        # This vector/line represents the trajectory of the bullet
        origin = (self._players[pid].posx, self._players[pid].posy)
        vector = (origin, origin + normalized_direction_vector * self._players[pid].weapon.range)
        line = LineString(vector)
        # First, check if we could even potentially shoot any player
        victims = []
        for p in self._players:
            # Yes, we do compute the player's hitbox on shoot. It is in fact lighter that storing it in the player, because storing it in the player's object would mean
            # updating it on every player's move. Here we do computation only on shoots, we are going to be many times less frequent that movements!
            hitbox = Point(p.posx,p.posy).buffer(Player.PLAYER_RADIUS)
            if line.intersects(hitbox): # hit!
                victims.append(p)

        # Then, if yes, check that there is not any obstacle to that shoot
        # Only check on obstacles that are close to that shoot's trajectory (that is to say, not < (x,y) (depending on the angle, could be not > (x,y) or event more complex cases, but that's the idea)))
        if 0 != len(victims):
            if not self._shoot_collide_with_obstacle(vector, line): # no collision with any obstacle, thus we can harm the victim
                self._harm_first_victim(victims, self._players[pid])

    stepx = const.CELL_SIZE
    stepy = const.CELL_SIZE

    # @param{list<Player>} victims : The list of people that could take the bullet (not sorted, we will have to find which one to harm)
    # @param{Player} shooter : Player object (will give us the weapong to harm the victim and the original position of the shoot, to find who to harm)
    def _harm_first_victim(self, victims, shooter): # @TODO
        pass

    def _shoot_collide_with_obstacle(self, vector, geometric_line): # @TODO
        x = (vector[0][0] // const.CELL_SIZE) * cons.CELL_SIZE # x origin, discretize to respect map's tiles (as, we will needs the true coordinates of the obstacle, when we'll find one)
        while x < vector[1][0]: # x end
            y = (vector[0][1] // const.CELL_SIZE) * cons.CELL_SIZE # y origin, same process as for x
            while y < vector[1][1]: # y end
                if self.slmap.is_obstacle_from_cell_coords(x, y):
                    obstacle = utils.create_square_from_top_left_coords(x, y) # Construct the obstacle
                    if geometric_line.intersects(obstacle): # Is the obstacle in the way of the bullet?
                        return True # Yes!
                y += self.stepy
            x += self.stepx
        return False

    def shutdown(self, force=False):
        self._loop.set()
