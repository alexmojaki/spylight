#!/usr/bin/env python

import sys
import unittest
sys.path.append("../")

import common.game_constants as const
from common.utils import mt
from server.game_engine import Player
from server.game_engine import GunWeapon

from server.game_engine import GameEngine

DBG = False

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

    def __check_is_harmed(self, player, original_health):
        self.assertTrue(player.hp < original_health, "The player should have been shot and lost HP but has not (hp, orig_hp)=" + str((player.hp, original_health)))

    def __check_is_not_harmed(self, player, original_health):
        self.assertTrue(player.hp == original_health, "The player should NOOOOOT have been shot (hp, orig_hp)=" + str((player.hp, original_health)) + ". The shot should have been stopped by an obstacle.")

    def test_easy_straight_horizontal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 2), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((7, 2), const.CELL_SIZE)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_obstructed_straight_horizontal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
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
        (p2.posx, p2.posy) = mt((7, 2), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

    def test_obstructed_straight_diagonal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
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
        (p2.posx, p2.posy) = mt((7, 3), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 6), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((7, 6), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall_2(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 6), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((6, 6), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall_3(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 6), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((5, 6), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_not_aiming(self): # TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        players = self.__gp(ge, "__players")
        id_p1, id_p2 = 0, 1
        p1, p2 = Player(id_p1, 0), Player(id_p2, 1)
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 0
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 6), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((7, 6), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        players[id_p1] = p1
        players[id_p2] = p2
        ge.shoot(id_p1, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

    def __setup_players(self, ge, positions):
        players = self.__gp(ge, "__players")
        n = len(positions) # the number of players
        middle = n/2+1
        _range, angle_error, dps = 10000, 0.0, 10
        for pid in xrange(0, n):
            player = Player(pid, pid // middle)
            player.weapon = GunWeapon(_range, angle_error, dps)
            (player.posx, player.posy) = mt(positions[pid], const.CELL_SIZE)
            players[pid] = player
        return players

    def test_simplistic_action_does_not_crash(self):
        self.map_file = "map_test_action.hfm"
        ge = self.getGE()
        players = self.__setup_players(ge, [(2, 6)])
        ge.action(players[0].player_id)

    def test_simplistic_action_no_action_to_take(self):
        self.map_file = "map_test_action.hfm"
        ge = self.getGE()
        players = self.__setup_players(ge, [(2, 6)])
        self.assertTrue(ge.action(players[0].player_id) is False, "There should not have been anything to do here.")

    def test_simplistic_action_terminal(self):
        self.map_file = "map_test_action.hfm"
        ge = self.getGE()
        players = self.__setup_players(ge, [(3, 3)])
        self.assertTrue(ge.action(players[0].player_id) is True, "There should have been something to activate (a terminal).")

    def test_simplistic_move(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        posx, posy, speedx, speedy, move_angle = 3, 3, 100, 100, 45
        players = self.__setup_players(ge, [(posx, posy)])
        pid = players[0].player_id
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        self.assertTrue(players[0].posx != posx and players[0].posy != posy, "The playe coordinates should have changed.")

if __name__ == '__main__':
    unittest.main()