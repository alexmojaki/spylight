#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Event, Lock, Timer
from time import time

from config_handler import ConfigHandler
from config_helper import default_config, option_types
from common.map_parser import SpyLightMap

import common.game_constants as const
import common.utils as utils
from math import sin, cos, sqrt, radians, degrees
from random import choice, uniform as rand
from shapely.geometry import Point, LineString
from shapely.occlusion import occlusion # Specific shapely version, here: https://github.com/tdubourg/Shapely/
from numpy import array, matrix # Will replace tuples for vectors operations (as (1, 1) * 2 = (1, 1, 1, 1) instead of (2, 2))
import logging

_logger = logging.getLogger("ge.log")
_logger.addHandler(logging.FileHandler("ge.log"))
_logger.setLevel(logging.INFO)


# ----------------- players related ---------------

class Player(object):
    """Player class"""
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
        self.max_speedx = 0   # /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work
        self.speedy = 0
        self.max_speedy = 0   # /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work
        self.move_angle = 0
        self.lifes = 0
        self.hp = 0
        self.sight_range = 0
        self.status = Player.STATUS_ALIVE
        self.weapon = None
        self.nickname = None  # Updated when a client connects to the server
        self.connected = False  # Indicate if a client is using this player

        # Occlusion related things
        self.sight_vertices = []
        self.obstacles_in_sight = []    # List of obstacle to be taken into account for occlusion computation
        self.obstacles_in_sight_n = 0   # basically, len(self.obstacles_in_sight)
        self.sight_angle = 0            # the direction to wich the player is looking
        self.sight_polygon_coords = []  # original polygon, the "raw" sight polygon, without occlusion
        self.visible_objects = []       # objects that this player can see (after applying occlusion)
        self.visible_players = []       # other players that this player can see (after applying occlusion)
        self.occlusion_polygon = None   # The shapely polygon computed by the occlusion. Will be used to compute intersections with various objects

        # Occlusion and collisions related
        self.hitbox = None

        # Some other things needed to initialize our object
        self.compute_hitbox()


    def take_damage(self, damage_amount):
        self.hp -= damage_amount # TODO change simplistic approach?
        if self.hp <= 0:
            self.status = Player.STATUS_DEAD

    def get_state(self):
        return {'l': self.lifes, 'hp': self.hp, 'x': self.posx, 'y': self.posy,
                'd': degrees(self.sight_angle), 's': self.status, 'v': self.
                sight_vertices, 'vp': self.visible_players, 'vo': self.
                visible_objects, 'ao': []}

    def add_new_visible_object(self, obj):
        if isinstance(obj, ActionableItem) is True:
            self.visible_objects.append((obj.type, obj.posx, obj.posy))

    def compute_hitbox(self):
        """This methods recomputes the hitbox attribute (Shapely Polygon) used by occlusion and collisions/shoots"""
        self.hitbox = Point(self.posx, self.posy).buffer(Player.PLAYER_RADIUS)

    def __str__(self):
        res = "Player of team=" + str(self.team) + ", id=" + str(self.player_id) + " at position (" + str(self.posx) + ", " + str(self.posy) + ")"
        res += ", hp=" + str(self.hp)
        return res

    def __repr__(self):
        return str(self)

class SpyPlayer(Player):
    """A Player that is a spy"""
    def __init__(self, player_id):
        super(SpyPlayer, self).__init__(player_id, const.SPY_TEAM)
        self.max_speedx = const.MAX_SPY_SPEED
        self.max_speedy = const.MAX_SPY_SPEED
        self.hp = const.MAX_SPY_HP
        self.sight_range = const.SPY_SIGHT_RANGE
        self.sight_polygon = Point(self.posx, self.posy).buffer(self.sight_range)
        self.__orig_posx = self.posx
        self.__orig_posy = self.posy
        self.sight_polygon_coords = []
        self.compute_sight_polygon_coords()
        self.weapon = SpyGunWeapon()

    def compute_sight_polygon_coords(self):
        # We are computing the translation of the circle from its creation to the current position
        # dx, dy are the delta between original position and current one
        # and we apply those delta to every circle's point
        # This is a circle, no rotation!
        dx, dy = self.posx - self.__orig_posx, self.posy - self.__orig_posy
        self.sight_polygon_coords = []
        for x,y in self.sight_polygon.exterior.coords:
            self.sight_polygon_coords.append((int(x + dx), int(y + dy)))

    def get_state(self):
        gs = super(SpyPlayer, self).get_state()
        gs['recap'] = []
        return gs

    def __str__(self):
        return super(MercenaryPlayer, self).__str__()

    def __repr__(self):
        return str(self)

class MercenaryPlayer(Player):
    """A Player that is a Mercenary"""
    def __init__(self, player_id):
        super(MercenaryPlayer, self).__init__(player_id, const.MERC_TEAM)
        self.max_speedx = const.MAX_MERC_SPEED
        self.max_speedy = const.MAX_MERC_SPEED
        self.hp = const.MAX_MERC_HP
        self.sight_range = const.MERC_SIGHT_RANGE
        self.weapon = MercGunWeapon()

    def compute_sight_polygon_coords(self):
        r = radians(self.sight_angle)
        cos_r, sin_r = cos(r), sin(r)
        self.sight_polygon_coords = (matrix([[cos_r, -sin_r], [sin_r, cos_r]]) * matrix([[self.posx, self.posx - self.sight_range/2, self.posx + self.sight_range/2], [self.posy, self.posy + self.sight_range, self.posy + self.sight_range]])).transpose().tolist()

    def get_state(self):
        gs = super(MercenaryPlayer, self).get_state()
        gs['kills'] = []
        return gs

    def __str__(self):
        return super(MercenaryPlayer, self).__str__()

    def __repr__(self):
        return str(self)

# ----------------- weapons related ---------------

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

class SpyGunWeapon(GunWeapon):
    """Gun for the Spy"""
    def __init__(self):
        super(SpyGunWeapon, self).__init__(const.SPY_GUN_RANGE,
            const.SPY_GUN_ANGLE_ERROR,
            const.SPY_GUN_DPS)

class MercGunWeapon(GunWeapon):
    """Gun for the Merc"""
    def __init__(self):
        super(MercGunWeapon, self).__init__(const.MERC_GUN_RANGE,
            const.MERC_GUN_ANGLE_ERROR,
            const.MERC_GUN_DPS)

class MineWeapon(Weapon):
    """Simplistic Mine Weapon implementation"""
    def __init__(self):
        super(MineWeapon, self).__init__()
        self.dps = const.MINE_DPS

# ----------------- visible objects related ---------------

class VisibleObject(object):
    """An object that can be viewed by a player"""
    def __init__(self, x, y):
        super(VisibleObject, self).__init__()
        self.posx = x
        self.posy = y
        self.type = const.ITEMS_TYPE_IDS['unkown'] # has to be overwritten by children

    def update(self):
        """
            This method has to be overriden by children classes.
            This method's purpose is to update the state of the object. For instance if
            an object has to evolve over time...
            There will be no time parameter so it is up to the object itself to store its creation time
            and compute by itself the detla between now() and its creation.
        """
        return self

    def update(self):
        """
            This method has to be overriden by children classes.
            This method's purpose is to update the state of the object. For instance if
            an object has to evolve over time...
            There will be no time parameter so it is up to the object itself to store its creation time
            and compute by itself the detla between now() and its creation.
        """
        return self

# ----------------- actionable items related ---------------

class ActionableItem(VisibleObject):
    """Simplistic ActionableItem implementation"""
    def __init__(self, *args):
        x, y = args
        super(ActionableItem, self).__init__(x, y)
        self.pos_row, self.pos_col = utils.norm_to_cell(x), utils.norm_to_cell(y)
        self.geometric_point = Point(x, y) # This will be used to compute intersections with the players' vision polygon

    def act(self, originPlayer):
        """
        Acts on the ActionableItem. If no action is available for the current player
        it will return False.
        Else, if there is an action to be done
        and this action has just been done
        if will return True
        """
        return False

class TerminalAI(ActionableItem):
    def __init(self, *args):
        """
            TerminalAI class: Terminal ActionableItem. Terminal are piratable by spies only.
        """
        super(TerminalAI, self).__init__(*args)
        self.type = const.ITEMS_TYPE_IDS['terminal']

# ----------------- proximity objects related ---------------

class ProximityObject(VisibleObject):
    """
    A ProximityObject is a VisibleObject that does something when
    a given player is in a gien range of it
    range is in real coordinates (not related to map cells size)
    """
    def __init__(self, *args):
        _range_of_action, x, y = args
        super(ProximityObject, self).__init__(x, y)
        self.pos_row, self.pos_col = utils.norm_to_cell(x), utils.norm_to_cell(y)
        self.geometric_point = Point(x, y) # This will be used to compute intersections with the players' vision polygon
        self.range_of_action = _range_of_action
        self.weapon = None # has to be overwritten by children

    def activate(self, player):
        """
        Activates/Enables on the ProximityObject.
        - If no action is available for the current player (because it is too far or anything else)
        AND it will return False.

        - Else, if there is an action to be done
        and this action has just been done
        AND it will return True
        """
        return False

# ----------------- Mixed ones -----------------

class MineAIPO(ActionableItem, ProximityObject):
    """simplistic Mine implementation"""
    def __init__(self, *args):
        new_args = [const.MINE_BOMB_ACTIVATION_RANGE]
        new_args.extends(args)
        super(MineAIPO, self).__init__(*new_args)
        self.type = const.ITEMS_TYPE_IDS['mine']
        # ProximityObject's related
        self.weapon = MineWeapon()

    # ActionableItem's related
    def act(self, originPlayer):
        if originPlayer.team == Player.SPY_TEAM: # and utils.distance((originPlayer.posx, originPlayer.posy), (self.posx, self.posy)): <-- was in the idea of having a range in which we can activate this thing, for later maybe
            # Deactivate the current mine
            GameEngine().remove_new_actionable_item(self) # Example of acting back with the GameEngine
            return True
        else:
            return False

    def activate(self, player):
        dist = utils.dist(((self.pos_col + 0.5) * const.CELL_SIZE, (self.pos_row + 0.5) * const.CELL_SIZE), (player.posx. player.posy))
        if type(player) is SpyPlayer and dist <= self.range_of_action: # If a spy is in range for bombing him
            self.weapon.damage(player) # Then, bomb him
            GameEngine().remove_new_actionable_item(self) # And... ourselves at the same time
            return True # TODO: Catch this return value in the GameEngine to send the bomb event to clients
        else:
            return False

# ----------------- ! GAME ENGINE ! ---------------

class GameEngine(object):
    _instances = {}

    def __new__(cls, *args, **kargs):
        if GameEngine._instances.get(cls) is None:
            GameEngine._instances[cls] = object.__new__(cls, *args, **kargs)
        return GameEngine._instances[cls]

    def init(self, config_file, map_file=None):
        self.__actionable_items = {} # Will contain the ActionableItem objects on the map that can do something when a player does 'action' on them (action = press the action key)
        self.__proximity_objects = {} # Will contain the ProximityObject objects on the map that can do something when a player is in a given range of them
        self.__loop = Event()
        self.__curr_player_number = 0
        self.__lock = Lock()
        self.__start_time = None
        self.__stepper_busy = Event()
        self.__stepper_interval = -1
        self.__stepper = None
        self.__end_time = -1
        self.all_players_connected = Event()
        self.load_config(config_file)
        self.auto_mode = False
        if map_file is not None:
            self.load_map(map_file)
        else:
            self.load_map(self.config.map_file)
        # will look like this : {"x,y": [item1, item2, item3]} (yes, there could potentially be multiple objects at the exact same position...)
        return self # allow chaining

    def acquire(self, blocking=1):
        self.__lock.acquire(blocking)

    def release(self):
        self.__lock.release()

    def setup_stepper(self, interval):
        def _stepper_action():
            self.__stepper = Timer(self.__stepper_interval, _stepper_action)
            self.__stepper.start()

            if not self.__stepper_busy.is_set():
                self.__stepper_busy.set()
                self.step()
                self.__stepper_busy.clear()

        if self.__stepper is not None:
            self.__stepper.cancel()
            self.__stepper_interval = -1
            self.__stepper = None

        if interval > 0:
            self.__stepper_interval = interval
            self.__stepper = Timer(interval, _stepper_action)
            self.__stepper.start()

    # @function push_new_item will register a new ActionableItem on the current game's map
    # @param item
    def push_new_item(self, item):
        key = self.__map_item_key_from_row_col(item.pos_row, item.pos_col)
        if isinstance(item, ActionableItem):
            dict_ = self.__actionable_items
        elif isinstance(item, ProximityObject):
            dict_ = self.__proximity_objects
        else:
            return self # allow chaining
        try:
            dict_[key].append(item)
        except KeyError:
            dict_[key] = [item]
        return self # allow chaining

    def remove_new_actionable_item(self, item):# TODO implementation of that
        return self # allow chaining

    def end_of_game(self):
        self.__loop.set()

    @property
    def loop(self):
        return not self.__loop.is_set()

    def step(self):
        # TODO: Maybe re-write the following lines, for a better handling of
        #       game termination.
        if self.auto_mode and self.__game_finished():
            self.end_of_game()
            return

        # Update players' positions and visions
        for p in self.__players:
            normalized_array = self.__get_normalized_direction_vector_from_angle(p.move_angle)
            self.__move_player(p, normalized_array[0] * p.speedx, normalized_array[1] * p.speedy)
            p.obstacles_in_sight = []
            p.obstacles_in_sight_n = 0
            # ------- Update player's sight -------
            # Parametrize things for occlusion (get obstacles that need to be taken into account by occlusion)
            sight_direction = self.__get_normalized_direction_vector_from_angle(p.sight_angle) * p.sight_range
            # A bit bruteforce here, let's use a circle instead of the real shaped vision
            # Just because there won't be many items to go through anyway
            # and for simplicity's and implementation speed's sakes
            y_start = max(0, p.posy - p.sight_range)
            y_end = min(self.slmap.max_y, p.posy + p.sight_range)
            x_start = max(0, p.posx - p.sight_range)
            x_end = min(self.slmap.max_x, p.posx + p.sight_range)
            row_start   = utils.norm_to_cell(y_start)
            row_end     = utils.norm_to_cell(y_end)
            col_start   = utils.norm_to_cell(x_start)
            col_end     = utils.norm_to_cell(x_end)
            vect = ((x_start, y_start), (x_end, y_end))
            self.__for_obstacle_in_range(vect, self.__occlusion_get_obstacle_in_range_callback, player=p)
            p.compute_sight_polygon_coords()
            # Launch occlusion
            p.sight_vertices, p.occlusion_polygon = occlusion(p.posx, p.posy, p.sight_polygon_coords, p.obstacles_in_sight, p.obstacles_in_sight_n)

            # ---------- Update player's visible objects list ----------
            # Note: Here we only go through the visible objects that are in a given range, not through all of them
            # We will go through the complete list, in order to update them, later in this method
            del p.visible_objects[:] # Empty the list

            for row in xrange(row_start, row_end+1):
                for col in xrange(col_start, col_end+1):
                    try:
                        for item in self.__actionable_items[self.__map_item_key_from_row_col(row, col)]:
                            if p.occlusion_polygon.intersects(item.geometric_point):
                                p.add_new_visible_object(item)
                    except KeyError:
                        pass # There was nothing at this (row,col) position...
                    try:
                        for item in self.__proximity_objects[self.__map_item_key_from_row_col(row, col)]:
                            if p.occlusion_polygon.intersects(item.geometric_point):
                                p.add_new_visible_object(item)
                    except KeyError:
                        pass # There was nothing at this (row,col) position...

            # ---------- Update player's visible players list ----------

            del p.visible_players[:] # Empty the list
            # Re-populate it
            for p2 in self.__players:
                if p2 is p:
                    continue # Do not include ourself in visible objects
                if p.occlusion_polygon.intersects(p2.hitbox):
                    p.visible_players.append((p2.player_id, p2.posx, p2.posy, p2.move_angle))
        # end of by player loop

        # Now go through all of the visible items to update them
        for row in xrange(0, self.slmap.height):
            for col in xrange(0, self.slmap.width):
                try:
                    for item in self.__actionable_items[self.__map_item_key_from_row_col(row, col)]:
                        item.update()
                except KeyError:
                    pass # There was nothing at this (row,col) position...
                try:
                    for item in self.__proximity_objects[self.__map_item_key_from_row_col(row, col)]:
                        item.update()
                        # Try to activate the proximity object on this player
                        for p_ in self.__players:
                            item.activate(p_)
                except KeyError:
                    pass # There was nothing at this (row,col) position...


    def __game_finished(self):
        # Note: This function is the right place to set end time of the
        #       game, because it knows the cause of the termination. If time is
        #       over, we must adapt the end time calculation to ensure it is
        #       accurate (i.e. we cannot trust time()). In all the other cases,
        #       end time is current time (i.e. time() value).

        # TODO: The end of the time is obviously not the only cause of game
        #       termination. Other causes should be handled too.
        if self.get_remaining_time() <= 0:
            self.__end_time = self.__start_time + self.__total_time
            return True
        else:
            return False

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

        # Do not go out of the map please :

        if x_to_be > self.slmap.max_x:
            x_to_be = self.slmap.max_x

        if y_to_be > self.slmap.max_y:
            y_to_be = self.slmap.max_y

        if x_to_be < 0:
            x_to_be = 0

        if y_to_be < 0:
            y_to_be = 0

        row, col = utils.norm_to_cell(player.posy), utils.norm_to_cell(player.posx)
        row_to_be, col_to_be = utils.norm_to_cell(y_to_be), utils.norm_to_cell(x_to_be)

        is_obs_by_dx = self.slmap.is_obstacle_from_cell_coords(row, col_to_be)
        is_obs_by_dy = self.slmap.is_obstacle_from_cell_coords(row_to_be, col)
        if is_obs_by_dx is False and is_obs_by_dy is False: # no collision
            player.posx = x_to_be
            player.posy = y_to_be
        elif is_obs_by_dx is False: # no collision only for x displacement
            player.posx = x_to_be
            player.posy = row_to_be * const.CELL_SIZE - 1 # maximum possible posy before colliding
        elif is_obs_by_dy is False: # no collision only for y displacement
            player.posy = y_to_be
            player.posx = col_to_be * const.CELL_SIZE - 1 # maximum possible posx before colliding
        else: # collision along all axis
            player.posx = col_to_be * const.CELL_SIZE - 1 # maximum possible posx before colliding
            player.posy = row_to_be * const.CELL_SIZE - 1 # maximum possible posy before colliding

        player.compute_hitbox()

        return player # allow chaining

    def __occlusion_get_obstacle_in_range_callback(self, vector, row, col, **kwargs):
        p = kwargs['player']
        x, y = col * const.CELL_SIZE, row * const.CELL_SIZE
        p.obstacles_in_sight.extend(
            [x, y,
            x + const.CELL_SIZE, y,
            x + const.CELL_SIZE, y + const.CELL_SIZE,
            x, y + const.CELL_SIZE])
        p.obstacles_in_sight_n += 8
        return None # just to explicitely tell the calling function to continue (I hate implicit things)


    def __map_item_key_from_row_col(self, row, col):
        return str(row) + "," + str(col)

    def get_player_sight(self, pid):
        return self.__players[pid].sight_vertices

    def action(self, pid):
        """

        :param pid: id of the player that is "actioning" (doing "action" action)
        :return: True of there was something to do, False else
        """
        actioner = self.__players[pid]
        key = self.__map_item_key_from_row_col(actioner.posx // const.CELL_SIZE, actioner.posy // const.CELL_SIZE)
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
        print "load_map: Loading map_file" + str(map_file)
        self.slmap = SpyLightMap()
        self.slmap.load_map(map_file)
        # Go through the whole map to find for special things to register, like actionable items...
        for row in xrange(0, self.slmap.height):
            for col in xrange(0, self.slmap.width):
                if self.slmap.map_tiles[row][col] == self.slmap.TERMINAL_KEY:
                    terminal = TerminalAI(row * const.CELL_SIZE, col * const.CELL_SIZE)
                    self.push_new_item(terminal)

        self.__total_time = 600  # TODO: Update with the real time read from the map file.
        self.__max_player_number = 1  # TODO: Update with the true player number
                                      #       read from the map file.
        # Loading players
        start_merc_pids = 0 # firt merc pid to be assigned
        end_merc_pids = max(0, self.slmap.nb_players[0]-1) # Last mercernary pid to be assigned
        start_spy_pids = end_merc_pids+1 # firt spy pid to be assigned
        end_spy_pids = max(start_merc_pids, start_spy_pids + self.slmap.nb_players[1]-1) # Last spy pid to be assigned
        self.__players = [MercenaryPlayer(i) for i in xrange(start_merc_pids, end_merc_pids+1)] # TODO: replace that by the actual player loading
        self.__players.extend([SpyPlayer(i) for i in xrange(start_spy_pids, end_spy_pids+1)]) # TODO: replace that by the actual player loading

        # Move players to their respective spawn location
        for p in self.__players:
            spawn = self.slmap.get_spawn_point(p.team, p.player_id)
            dx, dy = spawn[1] * const.CELL_SIZE, spawn[0] * const.CELL_SIZE
            self.__move_player(p, dx, dy)
        # Do some things like settings the weapon for each player...
        return self # allow chaining

    def connect_to_player(self, team, nickname):
        if self.all_players_connected.is_set():
            return None

        self.acquire()

        players = [p for p in self.__players if not p.connected and p.team ==
            team]

        if len(players) > 1:
            player = choice(players)
        elif len(players) == 1:
            player = players[0]
        else:
            self.release()
            return None

        player.connected = True
        player.nickname = nickname
        self.__curr_player_number += 1
        if self.__curr_player_number == self.__max_player_number:
            self.start_auto_mode()

        self.release()

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

    def get_remaining_time(self):
        if self.__end_time > 0:
            return 0
        else:
            return max(int(round(self.__total_time - time() + self.
                                 __start_time)), 0)

    def get_current_time(self):
        if self.__end_time > 0:
            return int(round(self.__end_time - self.__start_time))
        else:
            return min(int(round(time() - self.__start_time)), self.
                                 __total_time)

    def get_game_statistics(self):
        # TODO: Return the game statistics useful to build the `end` frame.
        return {'winners': Player.SPY_TEAM, 'ttime': int(round(self.
                __start_time - time()))}

    def start_auto_mode(self):
        """
            This method will enable the "auto_mode"
            When auto_mode is enabled, the GameEngine will execute a step() every once a while
            This interval is controlled by self.config.step_state_interval

        :return: Nothing
        """
        self.auto_mode = True
        self.__loop.clear()
        self.setup_stepper(self.config.step_state_interval)
        self.__start_time = time()
        self.all_players_connected.set()
        return self # allow chaining

    def set_sight_angle(self, pid, angle):
        self.__players[pid].sight_angle = radians(angle)
        return self # allow chaining

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
        :param percentage: (real) between 0 and 1, percentage of its maximum speed along this axis,
        after taking into account the angular direction (this is like a speed modifier)
        """
        p = self.__players[pid]
        p.speedx = percentage * p.max_speedx
        return self

    def set_movement_speedy(self, pid, percentage):
        """
        Set the speed of a given player, on the y axis

        :param pid: Player id (int)
        :param percentage: (real) between 0 and 1, percentage of its maximum speed along this axis,
        after taking into account the angular direction (this is like a speed modifier)
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
            hitbox = p.hitbox
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
        col_orig = utils.norm_to_cell(vector[0][0]) # x origin, discretize to respect map's tiles (as, we will needs the true coordinates of the obstacle, when we'll find one)
        _logger.info("__shoot_collide_with_obstacle(): x=" + str(col_orig))
        row = utils.norm_to_cell(vector[0][1]) # y origin, same process as for x
        _logger.info("__shoot_collide_with_obstacle(): y=" + str(row))
        col_end = int(utils.norm_to_cell(vector[1][0]))
        row_end = int(utils.norm_to_cell(vector[1][1]))
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

    def stop_auto_mode(self, force=False):
        """
        Will disable auto_mode.
        :param force:
        :return:
        """
        if self.loop:
            self.end_of_game()
        self.setup_stepper(-1)  # Disable stepping
        return self # allow chaining
