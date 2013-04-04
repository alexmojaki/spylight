#!/usr/bin/env python

import sys
import unittest
sys.path.append("../")

import common.game_constants as const
from common.utils import mt
from server.game_engine import Player
from server.game_engine import GunWeapon

from server.game_engine import GameEngine

DBG = True

class GameEngineTest(unittest.TestCase):
    """Tests for GameEngine class"""
    def setUp(self):
        self.conf_file = "conf_test.ini"
        self.map_file = "map_test.hfm"

    def getGE(self):
        return GameEngine().init(self.conf_file, self.map_file)
    
    # This is dangerous, do not attempt at home
    # This is used to access private stuff easily
    # testing purposes only
    def __get_private(self, obj, name):
        return getattr(obj, "_" + obj.__class__.__name__ + name)

    # Just an alias for __get_private, because the original name is too damn long
    # but this stuff being what it is, I don't want it to have another
    # name that would not document it
    def __gp(self, o, n):
        return self.__get_private(o, n)
        
    def test_instanciate(self):
        self.getGE()

    def test_load_config_1(self):
        ge = self.getGE()
        self.assertTrue(ge.config is not None, "The config of the GameEngine was not loaded successfully and is None")

    def test_load_config(self):
        ge = self.getGE()
        self.assertTrue(ge.config.send_state_interval == 0.02)

    def test___actionable_item_key_from_row_col(self):
        ge = self.getGE()
        result = self.__gp(ge, "__actionable_item_key_from_row_col")(1, 2)
        expected = "1,2"
        self.assertTrue(result == expected)
    
    def test_easy_straight_horizontal_line_shoot(self):
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 0), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((8, 0), const.CELL_SIZE)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.assertTrue(p2.hp < original_health, "The player should have been shot and lost HP but has not.")

    def test_obstructed_straight_horizontal_line_shoot(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 2), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((8, 2), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.assertTrue(p2.hp == original_health, "The player should not have been shot. The shot should have been stopped by an obstacle.")
        self.map_file = "map_test.hfm"



if __name__ == '__main__':
    unittest.main()