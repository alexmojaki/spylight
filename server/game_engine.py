#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event, Lock

from config_handler import ConfigHandler
from config_helper import default_config, option_types
from common.map_parser import SpyLightMap

import common.game_constants as const
import common.utils as utils
from math import sin, cos, sqrt, radians
from random import choice, uniform as rand
from shapely.geometry import Point, LineString
from shapely.occlusion import occlusion # Specific shapely version, here: https://github.com/tdubourg/Shapely/
from numpy import array # Will replace tuples for vectors operations (as (1, 1) * 2 = (1, 1, 1, 1) instead of (2, 2))
import logging

_logger = logging.getLogger("ge.log")
_logger.addHandler(logging.FileHandler("ge.log"))
_logger.setLevel(logging.INFO)

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
        self.team = team
        self.posx = 0
        self.posy = 0
        self.speedx = 0
        self.max_speedx = 100 # TODO: Change that, pass as constructor value or any other thing
        self.speedy = 0
        self.max_speedy = 100 # TODO: Change that, pass as constructor value or any other thing
        self.move_angle = 0
        self.hp = 100 # TODO: Change that, pass as constructor value or any other thing
        self.sight_range = 200 # TODO: Change that, pass as constructor value or any other thing
        self.status = Player.STATUS_ALIVE
        self.weapon = None
        self.nickname = None  # Updated when a client connects to the server
        self.connected = False  # Indicate if a client is using this player

        # Occlusion related things
        self.sight_vertices = []
        self.obstacles_in_sight = [] # List of obstacle to be taken into account for occlusion computation
        self.obstacles_in_sight_n = 0 # basically, len(self.obstacles_in_sight)
        self.sight_polygon_coords = []

    def take_damage(self, damage_amount):
        self.hp -= damage_amount # TODO change simplistic approach?
        if self.hp <= 0:
            self.status = Player.STATUS_DEAD
    def get_state(self):
        return {'hp': self.hp, 'x': self.posx, 'y': self.posy} # TODO: Actually put what we need here


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
    def __init__(self, row, col):
        super(ActionableItem, self).__init__()
        self.pos_row = row
        self.pos_col = col

    def act(self, originPlayer):
        pass # Todo implement that

class MineAI(ActionableItem):
    """simplistic Mine implementation"""
    def __init__(self, **kwargs):
        super(MineAI, self).__init__(kwargs)

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


class TerminalAI(ActionableItem):
    def __init(self, **args):
        """
            TerminalAI class: Terminal ActionableItem. Terminal are piratable by spies only.
        """
        super(TerminalAI, self).__init__(args)


class GameEngine(object):
    _instances = {}

    def __new__(cls, *args, **kargs):
        if GameEngine._instances.get(cls) is None:
            GameEngine._instances[cls] = object.__new__(cls, *args, **kargs)
        return GameEngine._instances[cls]

    def init(self, config_file, map_file=None):
        self.__actionable_items = {} # Will contain the ActionableItem objects on the map that can do something when a player does 'action' on them (action = press the action key)
        self.__loop = Event()
        self.__curr_player_number = 0
        self.__player_connection = Lock()
        self.all_players_connected = Event()
        self.load_config(config_file)
        if map_file is not None:
            self.load_map(map_file)
        else:
            self.load_map(self.config.map_file)
        # will look like this : {"x,y": [item1, item2, item3]} (yes, there could potentially be multiple objects at the exact same position...)
        return self # allow chaining

    # @function push_new_actionable_item will register a new ActionableItem on the current game's map
    # @param{ActionableItem} item
    def push_new_actionable_item(self, item):
        key = self.__actionable_item_key_from_row_col(item.pos_row, item.pos_col)
        try:
            self.__actionable_items[key].append(item)
        except KeyError:
            self.__actionable_items[key] = [item]
        return self # allow chaining

    def remove_new_actionable_item(self, item):# TODO implementation of that
        return self # allow chaining

    def end_of_game(self):
        self.__loop.shutdown()

    @property
    def loop(self):
        return not self.__loop.is_set()

    def step(self):
        # Update player's positions
        for p in self.__players:
            normalized_array = self.__get_normalized_direction_vector_from_angle(p.move_angle)
            p.posx += normalized_array[0] * p.speedx
            p.posy += normalized_array[1] * p.speedy
            p.obstacles_in_sight = []
            p.obstacles_in_sight_n = 0
            # ------- Update player's sight -------
            # Parametrize things for occlusion (get obstacles that need to be taken into account by occlusion)
            sight_direction = self.__get_normalized_direction_vector_from_angle(p.move_angle) * p.sight_range
            vect = ((int(p.posx), int(p.posy)), tuple((p.posx + sight_direction[0], p.posy + sight_direction[1])))
            self.__for_obstacle_in_range(vect, self.__occlusion_get_obstacle_in_range_callback, player=p)
            # TODO: Someone with actual geometry skill to put triangle rotation by taking into account the angle, here
            p.sight_polygon_coords = [[p.posx, p.posy], [p.posx - p.sight_range/2, p.posy + p.sight_range], [p.posx + p.sight_range/2, p.posy + p.sight_range]]
            # Launch occlusion
            p.sight_vertices = occlusion(p.posx, p.posy, p.sight_polygon_coords, p.obstacles_in_sight, p.obstacles_in_sight_n)

    def __move_player(self, player, dx, dy):
        """

        Moves the given player using the given dx nd dy deltas for x and y axis
        taking into account collisions with obstacles 

        :param player: Instance of Player class, the player we want to move
        :param dx: float, the x coordinate difference we want to apply to the current player 
            (may or may not be pplied depending on wether there are collisions)
        :param dy: float, the y coordinate difference we want to apply to the current player 
            (may or may not be pplied depending on wether there are collisions)
        :return None
        """

        x_to_be, y_to_be = player.posx + dx, player.posy + dy
        row, col = self.__norm_to_cell(player.posy), self.__norm_to_cell(player.posx)
        row_to_be, col_to_be = self.__norm_to_cell(y_to_be), self.__norm_to_cell(x_to_be)
        is_obs_by_dx = self.slmap.is_obstacle_from_cell_coords(row, col_to_be)
        is_obs_by_dy = self.slmap.is_obstacle_from_cell_coords(row_to_be, col)
        if is_obs_by_dx is False and is_obs_by_dy is False: # no collision
            player.posx += dx
            player.posy += dy
        elif is_obs_by_dx is False: # no collision only for x displacement
            player.posx += dx
            player.posy = row_to_be * const.CELL_SIZE - 1 # maximum possible posy before colliding
        elif is_obs_by_dy is False: # no collision only for y displacement
            player.posy += dy
            player.posx = col_to_be * const.CELL_SIZE - 1 # maximum possible posx before colliding
        else:
            player.posx = col_to_be * const.CELL_SIZE - 1 # maximum possible posx before colliding
            player.posy = row_to_be * const.CELL_SIZE - 1 # maximum possible posy before colliding

    def __occlusion_get_obstacle_in_range_callback(self, vector, row, col, **kwargs):
        p = kwargs['player']

        p.obstacles_in_sight.extend(
            [col, row,
            col + const.CELL_SIZE, row,
            col + const.CELL_SIZE, row + const.CELL_SIZE,
            col, row + const.CELL_SIZE])
        p.obstacles_in_sight_n += 8
        return None # just to explicitely tell the calling function to continue (I hate implicit things)


    def __actionable_item_key_from_row_col(self, row, col):
        return str(row) + "," + str(col)

    def get_player_sight(self, pid):
        return self.__players[pid].sight_vertices

    def action(self, pid):
        """

        :param pid: id of the player that is "actioning" (doing "action" action)
        :return: True of there was something to do, False else
        """
        actioner = self.__players[pid]
        key = self.__actionable_item_key_from_row_col(actioner.posx // const.CELL_SIZE, actioner.posy // const.CELL_SIZE)
        try:
            objs = self.__actionable_items[key]
        except KeyError:
            return False
        # Arbitrary here: Take the first of the list to act on... (TODO: See if we want to make priorities)
        objs[0].act(actioner)
        return True

    def load_config(self, config_file):
        self.config = ConfigHandler(config_file, default_config, option_types)
        return self # allow chaining

    def load_map(self, map_file):
        self.__map_file = map_file
        self.slmap = SpyLightMap()
        self.slmap.load_map(map_file)
        # Go through the whole map to find for special things to register, like actionable items...
        for row in xrange(0, self.slmap.height):
            for col in xrange(0, self.slmap.width):
                if self.slmap.map_tiles[row][col] == self.slmap.TERMINAL_KEY:
                    terminal = TerminalAI(row, col)
                    self.push_new_actionable_item(terminal)

        self.__max_player_number = 4  # TODO: Update with the true player number
                                      #       read from the map file.
        # Loading players
        self.__players = [Player(i, Player.SPY_TEAM) for i in xrange(0, 2)] # TODO: replace that by the actual player loading
        self.__players.extend([Player(i, Player.MERC_TEAM) for i in xrange(2, 4)]) # TODO: replace that by the actual player loading
        # Do some things like settings the weapon for each player...
        return self # allow chaining

    def connect_to_player(self, team, nickname):
        if self.all_players_connected.is_set():
            return None

        self.__player_connection.acquire()

        players = [p for p in self.__players if not p.connected and p.team == \
            team]

        if len(players) > 1:
            player = choice(players)
        elif len(players) == 1:
            player = players[0]
        else:
            self.__player_connection.release()
            return None

        player.connected = True
        player.nickname = nickname
        self.__curr_player_number += 1
        if self.__curr_player_number == self.__max_player_number:
            self.all_players_connected.set()

        self.__player_connection.release()

        return player.player_id

    def get_map_name(self):
        return self.__map_file

    def get_map_title(self):
        return self.slmap.title

    def get_map_hash(self):
        return self.slmap.get_hash()

    def get_player_state(self, pid):
        return self.__players[pid].get_state()

    def get_nb_players(self):
        return self.__curr_player_number

    def get_players_info(self):
        return [(p.nickname, p.player_id, p.team) for p in self.__players]

    def start(self):
        self.__loop.clear()
        return self # allow chaining

    def set_sight_angle(self, pid, angle):
        return self.set_movement_angle(pid, angle)

    def set_movement_angle(self, pid, angle):
        """
        Set the movement angle ("kivy convention") of the given player.
        This angle will define in which direction the player is heading when it will have a speed assigned

        :param pid: Player id (int)
        :param angle: heading direction angle IN DEGREES (real or integer)
        """
        self.__players[pid].move_angle = radians(angle)
        return self # allow chaining

    def set_movement_speedx(self, pid, percentage):
        """
        Set the speed of a given player, on the xy axis

        :param pid: Player id (int)
        :param percentage: (real) between 0 and 1, percentage of its maximum speed along this axis
        """
        p = self.__players[pid]
        p.speedx = percentage * p.max_speedx
        return self

    def set_movement_speedy(self, pid, percentage):
        """
        Set the speed of a given player, on the y axis

        :param pid: Player id (int)
        :param percentage: (real) between 0 and 1, percentage of its maximum speed along this axis
        """
        p = self.__players[pid]
        p.speedy = percentage * p.max_speedy
        return self

    def __get_normalized_direction_vector_from_angle(self, a):
        x, y = -sin(a), cos(a)
        return (array((x, y)) / sqrt(x**2 + y**2))

    # @param pid player id
    # @param angle shoot angle, "kivy convention", in degree
    # @return{Player} the victim that has been shot, if any, else None
    def shoot(self, pid, angle):
        _logger.info("Starting shoot method")
        shooter = self.__players[pid]
        # Shoot "angle"
        a = radians(angle)
        # Weapon error angle application:
        a += shooter.weapon.draw_random_error()

        # Direction of the bullet (normalized vector)
        normalized_direction_vector = self.__get_normalized_direction_vector_from_angle(a) # x, y, but in the "kivy convention"

        # This vector/line represents the trajectory of the bullet
        origin = array((shooter.posx, shooter.posy))
        vector = (tuple(origin), tuple(origin + (normalized_direction_vector * shooter.weapon.range)))
        line = LineString(vector)

        _logger.info("origin=" + str(origin))
        _logger.info("vector=" + str(vector))

        # First, check if we could even potentially shoot any player
        victims = []
        for p in self.__players:
            if p == shooter:
                continue # you cannot shoot yourself
            # Yes, we do compute the player's hitbox on shoot. It is in fact lighter that storing it in the player, because storing it in the player's object would mean
            # updating it on every player's move. Here we do computation only on shoots, we are going to be many times less frequent that movements!
            hitbox = Point(p.posx, p.posy).buffer(Player.PLAYER_RADIUS)
            if line.intersects(hitbox): # hit!
                victims.append(p)

        # Then, if yes, check that there is not any obstacle to that shoot
        # Only check on obstacles that are close to that shot's trajectory (that is to say, not < (x,y) (depending on the angle, could be not > (x,y) or event more complex cases, but that's the idea)))
        if 0 != len(victims):
            distance, first_victim = self.__find_closest_victim(victims, shooter)
            # We re-compute the vector, stopping it at the victim's position. Indeed, if we used the "vector" variable
            # to look for collisions, as it uses the maximum weapon's range, we would look for collision BEHIND the
            # victim as well !
            to_first_victim_vector = (tuple(origin), tuple(origin + (normalized_direction_vector * distance)))
            if not self.__shoot_collide_with_obstacle(to_first_victim_vector, line): # no collision with any obstacle, thus we can harm the victim
                return self.__harm_victim(first_victim, shooter)
        else: # Else, there's just nothing to do, you did not aim at anyone, n00b
            return None

    stepx = const.CELL_SIZE
    stepy = const.CELL_SIZE

    def __find_closest_victim(self, victims, shooter):
        return sorted([(sqrt((shooter.posx - v.posx)**2 + (shooter.posy - v.posy)**2), v) for v in victims])[0] # Ugly line, huh? We create a list of (distance, victim) tuples, sort it (thus, the shortest distance will bring the first victim at pos [0] of the list


    # @param{Player} shooter : Player object (will give us the weapon to harm the victim and the original position of the shoot, to find who to harm)
    # @return{Player} t        # First, check if we could even potentially shoot any player
    # @return{Player} the victim harmed
    def __harm_victim(self, victim, shooter):
        shooter.weapon.damage(victim)
        return victim

    def __norm_to_cell(self, coord):
        return (coord // const.CELL_SIZE)

    def __for_obstacle_in_range(self, vector, callback, **callback_args):
        """
            Finds the obstacle in the given range (range = a distance range + an angle (factorized in the "vector" argument))
            and executes the callback for each found obstacle

            :param vector: range/direction vector, of the form ((x_orig, y_orig), (x_end, y_end)) in real map coordinates
            :param callback: callback function, signature must be func([self, ]vector, row, col, **kwargs)
            :param callback_args: Additional arguments that will be passed to the callback function when executed

            /!\ Important /!\ Returns:
                - None either if the callback was never called or if it never returned anything else than None
                - the callback value, if a callback call returns anything that is not None
        """
        col_orig = self.__norm_to_cell(vector[0][0]) # x origin, discretize to respect map's tiles (as, we will needs the true coordinates of the obstacle, when we'll find one)
        _logger.info("__shoot_collide_with_obstacle(): x=" + str(col_orig))
        row = self.__norm_to_cell(vector[0][1]) # y origin, same process as for x
        _logger.info("__shoot_collide_with_obstacle(): y=" + str(row))
        col_end = int(self.__norm_to_cell(vector[1][0]))
        row_end = int(self.__norm_to_cell(vector[1][1]))
        # The following variables will be used to increment in the "right direction" (negative if the end if lower
        # than the origin, etc....
        col_increment_sign = 1 if (col_end-col_orig) > 0 else -1
        row_increment_sign = 1 if (row_end-row) > 0 else -1
        # A bit of explanation of the conditions here :
        # row < self.slmap.height --> Self explanatory, do not go over the map (as the line is multiplied by a
        # coefficient, this check is necessary
        # (row-row_end) != row_increment_sign --> This means that we want to stop when the "row" variable has gone one
        # unit further than the row_end variable. row_increment_sign will always have the same sign as
        # (row-row_end) when row is one unit further than row_end (by further we mean : one iteration further, in the
        # "direction" in which we are iterating: that could be forward or backward). Stopping when we are "one further"
        # means that we iterate until we reach the row_end... INCLUDED! (else, would not work when perfectly aligned)
        # same thing for the condition with "row" replaced by "col"
        while row < self.slmap.height and (row-row_end) != row_increment_sign:
            col = col_orig
            while col < self.slmap.width and (col-col_end) != col_increment_sign:
                if self.slmap.is_obstacle_from_cell_coords(row, col):
                    callback_result = callback(vector, row, col, **callback_args)
                    if callback_result is not None:
                        return callback_result
                col += col_increment_sign * 1
            row += row_increment_sign * 1
        return None

    def __shoot_collide_with_obstacle(self, vector, geometric_line):
        if self.__for_obstacle_in_range(vector, self.__shoot_collide_with_obstacle_callback, geomatric_line=geometric_line) is not None:
            return True # Found some obstacle collision !
        return False # Did not found any obstacle collision

    def __shoot_collide_with_obstacle_callback(self, vector, row, col, **kwargs):
        geometric_line = kwargs['geomatric_line']
        obstacle = utils.create_square_from_top_left_coords(row*const.CELL_SIZE, col*const.CELL_SIZE, const.CELL_SIZE) # Construct the obstacle
        if geometric_line.intersects(obstacle): # Is the obstacle in the way of the bullet?
            return True # Yes!
        return None

    def shutdown(self, force=False):
        self.__loop.set()
        return self # allow chaining
