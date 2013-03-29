#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event

from config_handler import ConfigHandler
from config_helper import default_config, option_types
from common.map_parser import SpyLightMap

import common.game_constants as const
import common.utils as utils
from math import sin, cos, sqrt, radians
from random import uniform as rand
from shapely.geometry import Point, LineString

class Player(object):
    """Player class, mainly POCO object"""
    PLAYER_RADIUS = 5
    STATUS_ALIVE = 1
    STATUS_DEAD = 0
    SPY_TEAM = const.SPY_TEAM
    MERC_TEAM = const.MERC_TEAM

    def __init__(self, player_id, team):
        super(Player, self).__init__()
        self.player_id = player_id
        self.posx = 0 
        self.posy = 0 
        self.hp = 100 # TODO : Change that ?
        self.status = Player.STATUS_ALIVE
        self.weapon = None
        self.team = team

    def take_damage(self, damage_amount):
        self.hp -= damage_amount # TODO change simplistic approach?
        if self.hp <= 0:
            self.status = Player.STATUS_DEAD


class Weapon(object):
    """Weapong class, mainly a POCO object"""
    def __init__(self):
        super(Weapon, self).__init__()
        self.dps = 0 # damage per shoot #TODO: assign value using a constructor parameter?

    # @param{Player} victim: Victim to damage using this weapon
    def damage(self, victim):
        victim.take_damage(self.dps)


class GunWeapon(Weapon):
    """Simplistic Gun Weapon implementation"""
    def __init__(self, _range, angle_error, dps):
        super(GunWeapon, self).__init__()
        self.range = _range
        self.angle_error = angle_error # THE ANGLE IS IN RADIANS DUDES
        self.dps = dps

    def draw_random_error(self):
        return rand(-self.angle_error, self.angle_error)

class MineWeapon(Weapon):
    """Simplistic Mine Weapon implementation"""
    def __init__(self):
        super(MineWeapon, self).__init__()
        self.dps = 50
        

    
class ActionableItem(object):
    """Simplistic ActionableItem implementation"""
    def __init__(self, x, y):
        super(ActionableItem, self).__init__()
        self.posx = x
        self.posy = y

    def act(self, originPlayer):
        pass # Todo implement that
    
class MineAI(ActionableItem):
    """simplistic Mine implementation"""
    def __init__(self, x, y):
        super(MineAI, self).__init__(x, y)
    
    def act(self, originPlayer):
        if originPlayer.team == Player.SPY_TEAM:
            # Deactivate the current mine
            GameEngine().remove_new_actionable_item(self) # Example of acting back with the GameEngine

class ProximityObject(object):
    """docstring for ProximityObject"""
    def __init__(self, _range_of_action):
        super(ProximityObject, self).__init__()
        self.range_of_action = _range_of_action

class MinePO(ProximityObject):
    """docstring for MineProxObj"""
    def __init__(self, _range):
        super(MinePO, self).__init__(_range)
        self.weapon = MineWeapon()
        

class GameEngine(object):
    _instances = {}

    def __new__(cls, *args, **kargs):
        if GameEngine._instances.get(cls) is None:
            GameEngine._instances[cls] = object.__new__(cls, *args, **kargs)
        return GameEngine._instances[cls]

    def init(self, config_file, map_file):
        self.__loop = Event()
        self.load_config(config_file)
        self.load_map(map_file)
        self.__actionable_items = {} # Will contain the ActionableItem objects on the map that can do something when a player does 'action' on them (action = press the action key)
        # will look like this : {"x,y": [item1, item2, item3]} (yes, there could potentially be multiple objects at the exact same position...)

    # @function push_new_actionable_item will register a new ActionableItem on the current game's map
    # @param{ActionableItem} item
    def push_new_actionable_item(self, item):
        key = self.__actionable_item_key_from_row_col(item.posx // const.CELL_SIZE. item.posy // const.CELL_SIZE)
        try:
            self.__actionable_items[key].append(item)
        except KeyError:
            self.__actionable_items[key] = [item]

    def remove_new_actionable_item(self, item):# TODO implementation of that
        pass

    @property
    def loop(self):
        return not self.__loop.is_set()

    def __actionable_item_key_from_row_col(self, row, col):
        return str(row) + "," + str(col)
    
    def action(self, pid):
        actioner = self.__players[pid]
        key = self.__actionable_item_key_from_row_col(actioner.posx // const.CELL_SIZE, actioner.posy // const.CELL_SIZE)
        objs = self.__actionable_items[key]
        # Aribtray here: Take the first of the list to act on... (TODO: See if we want to make priorities)
        objs[0].act(actioner)

    def load_config(self, config_file):
        self.config = ConfigHandler(config_file, default_config, option_types)

    def load_map(self, map_file):
        self.slmap = SpyLightMap()
        self.slmap.load_map(map_file)
        self.__player_number = 4  # TODO: Update with the true player number
                                 #       read from the map file.
        # Loading players
        self.__players = [Player(i, Player.SPY_TEAM) for i in xrange(0, self.__player_number)] # TODO: replace that by the actual player loading
        # Do some things like settings the weapon for each player...

    def get_nb_players(self):
        return self.__player_number

    def start(self):
        self.__loop.clear()

    def updateMovementDir(self, pid, angle):
        self.__players[pid].movAngle = angle

    # @param pid player id
    # @param angle shoot angle, kivy convention, in degree
    # @return{Player} the victim that has been shot, if any, else None
    def shoot(self, pid, angle):
        shooter = self.__players[pid]
        # Shoot "angle"
        a = radians(angle)
        # Weapon error angle application:
        a += shooter.weapon.draw_random_error()
        
        # Direction of the bullet (normalized vector)
        normalized_direction_vector = (-sin(a), cos(a)) # x, y, but in the kivy convention
        
        # This vector/line represents the trajectory of the bullet
        origin = (shooter.posx, shooter.posy)
        vector = (origin, origin + normalized_direction_vector * shooter.weapon.range)
        line = LineString(vector)
        
        # First, check if we could even potentially shoot any player
        victims = []
        for p in self.__players:
            # Yes, we do compute the player's hitbox on shoot. It is in fact lighter that storing it in the player, because storing it in the player's object would mean
            # updating it on every player's move. Here we do computation only on shoots, we are going to be many times less frequent that movements!
            hitbox = Point(p.posx,p.posy).buffer(Player.PLAYER_RADIUS)
            if line.intersects(hitbox): # hit!
                victims.append(p)

        # Then, if yes, check that there is not any obstacle to that shoot
        # Only check on obstacles that are close to that shoot's trajectory (that is to say, not < (x,y) (depending on the angle, could be not > (x,y) or event more complex cases, but that's the idea)))
        if 0 != len(victims):
            if not self.__shoot_collide_with_obstacle(vector, line): # no collision with any obstacle, thus we can harm the victim
                return self.__harm_first_victim(victims, shooter)
        else: # Else, there's just nothing to do, you did not aim at anyone, n00b
            return None

    stepx = const.CELL_SIZE
    stepy = const.CELL_SIZE

    # @param{list<Player>} victims : The list of people that could take the bullet (not sorted, we will have to find which one to harm)
    # @param{Player} shooter : Player object (will give us the weapong to harm the victim and the original position of the shoot, to find who to harm)
    # @return{Player} the victim harmed
    def __harm_first_victim(self, victims, shooter): # @TODO
        first_victim = sorted([(sqrt((shooter.posx - v.posx)**2 + (shooter.posy - v.posy)**2), v) for v in victims])[0][1] # Ugly line, huh? We create a list of (distance, victim) tuples, sort it (thus, the shortest distance will bring the first victim at pos [0] of the list, then we get the [1] if the tuple to get the victim)
        shooter.weapon.damage(first_victim)
        return first_victim
        
    def __shoot_collide_with_obstacle(self, vector, geometric_line):
        x = (vector[0][0] // const.CELL_SIZE) * const.CELL_SIZE # x origin, discretize to respect map's tiles (as, we will needs the true coordinates of the obstacle, when we'll find one)
        while x < vector[1][0]: # x end
            y = (vector[0][1] // const.CELL_SIZE) * const.CELL_SIZE # y origin, same process as for x
            while y < vector[1][1]: # y end
                if self.slmap.is_obstacle_from_cell_coords(x, y):
                    obstacle = utils.create_square_from_top_left_coords(x, y) # Construct the obstacle
                    if geometric_line.intersects(obstacle): # Is the obstacle in the way of the bullet?
                        return True # Yes!
                y += self.stepy
            x += self.stepx
        return False

    def shutdown(self, force=False):
        self.__loop.set()
