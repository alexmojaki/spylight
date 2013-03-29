#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event

from config_handler import ConfigHandler

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
        self.config = ConfigHandler(config_file)
        self._player_number = 4  # TODO: Update with the true player number
                                 #       read from the map file.
        # Loading players
        self._players = [Player(i) for i in xrange(0, self._player_number)]
        # Do some things like settings the weapon for each player...

    def load_map(self, map_file):
        pass

    def get_nb_players(self):
        return self._player_number

    def start(self):
        self._loop.clear()

    def updateMovementDir(self, pid, angle):
        self._players[pid].movAngle = angle

    def shoot(self, pid, angle):
        # This vector/line represents the trajectory of the bullet
        vector = LineString(((self._players[pid].posx, self._players[pid].posy), (self._players[pid].posx + self._players[pid].weapon.range, self._players[pid].weapon.range)))
        # First, check if we could even potentially shoot any player
        victims = []
        for p in self._players:
            # Yes, we do compute the player's hitbox on shoot. It is in fact lighter that storing it in the player, because storing it in the player's object would mean
            # updating it on every player's move. Here we do computation only on shoots, we are going to be many times less frequent that movements!
            hitbox = Point(p.posx,p.posy).buffer(Player.PLAYER_RADIUS)
            if vector.intersects(hitbox): # hit!
                victims.append(p)

        # Then, if yes, check that there is not any obstacle to that shoot
        # Only check on obstacles that are close to that shoot's trajectory (that is to say, not < (x,y) (depending on the angle, could be not > (x,y) or event more complex cases, but that's the idea)))
        if 0 != len(victims):
                    

    def shutdown(self, force=False):
        self._loop.set()
