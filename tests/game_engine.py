#!/usr/bin/env python
from math import radians, cos

import sys
import unittest
sys.path.append("../")

import common.game_constants as const
from common.utils import mt
from server.game_engine import SpyPlayer, MercenaryPlayer
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

    def __setup_players(self, ge, positions):
        players = self.__gp(ge, "__players")
        # Empty all previously automatically loaded players
        del players[:]
        # And load our ones:
        n = len(positions) # the number of players
        players[:] = [None] * n
        middle = n/2+1
        _range, angle_error, dps = 10000, 0.0, 10
        for pid in xrange(0, n):
            if (pid // middle) == const.SPY_TEAM :
                player = SpyPlayer(pid)
            else:
                player = MercenaryPlayer(pid)
            (player.posx, player.posy) = mt(positions[pid], const.CELL_SIZE)
            players[pid] = player
            player.compute_hitbox()
        return players

    def test_instanciate(self):
        self.getGE()

    def test_load_config_1(self):
        ge = self.getGE()
        self.assertTrue(ge.config is not None, "The config of the GameEngine was not loaded successfully and is None")

    def test_load_config(self):
        ge = self.getGE()
        self.assertTrue(ge.config.send_state_interval == 0.02)

    def test___map_item_key_from_row_col(self):
        ge = self.getGE()
        result = self.__gp(ge, "__map_item_key_from_row_col")(1, 2)
        expected = "1,2"
        self.assertTrue(result == expected)

    def __check_is_harmed(self, player, original_health):
        self.assertTrue(player.hp < original_health, "The player should have been shot and lost HP but has not (hp, orig_hp)=" + str((player.hp, original_health)))

    def __check_is_not_harmed(self, player, original_health):
        self.assertTrue(player.hp == original_health, "The player should NOOOOOT have been shot (hp, orig_hp)=" + str((player.hp, original_health)) + ". The shot should have been stopped by an obstacle.")

    def test_easy_straight_horizontal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 2), (7, 2)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_obstructed_straight_horizontal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 2), (7, 2)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

    def test_obstructed_straight_diagonal_line_shoot(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 2), (7, 3)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 270 # shoot to the right of him
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 6), (7, 6)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        original_health = p2.hp
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall_2(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 6), (6, 6)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_in_hole_in_the_wall_3(self):# TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 6), (5, 6)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 271 # shoot to the right of him, BUT NOT EXACTLY 90 degrees to the right, as with angle errors we might shoot the cell on top of us because we are placed at the very limit of ou current cell
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_harmed(p2, original_health)

    def test_shot_not_aiming(self): # TODO: Refactor using __setup_two_players new method
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 6), (7, 6)])
        _range, angle_error, dps = 10000, 0.0, 10
        shoot_angle = 0
        p1.weapon, p2.weapon = GunWeapon(_range, angle_error, dps), GunWeapon(_range, angle_error, dps)
        original_health = p2.hp
        (p1.posx, p1.posy) = mt((2, 6), const.CELL_SIZE)
        (p2.posx, p2.posy) = mt((7, 6), const.CELL_SIZE)
        if DBG:
            print "Player1 pos=", (p1.posx, p1.posy)
            print "Player2 pos=", (p2.posx, p2.posy)
        ge.shoot(p1.player_id, shoot_angle)
        self.__check_is_not_harmed(p2, original_health)

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
        row, col = 3, 3
        posx, posy, speedx, speedy, move_angle = row*const.CELL_SIZE, col*const.CELL_SIZE, 1.0, 1.0, 315
        players = self.__setup_players(ge, [(col, row)])
        pid = players[0].player_id
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        self.assertTrue(players[0].posx != posx and players[0].posy != posy, "The playe coordinates should have changed.")

    def test_simplistic_move_with_speed_check(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy, move_angle = row*const.CELL_SIZE, col*const.CELL_SIZE, 1.0, 1.0, 315
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.8*const.CELL_SIZE
        p.max_speedy = 0.8*const.CELL_SIZE
        diagonal_move_reduc_coeff = cos(radians(45))
        expected_posx, expected_posy = posx + speedx * diagonal_move_reduc_coeff * p.max_speedx, posy + speedy * diagonal_move_reduc_coeff * p.max_speedy
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        self.assertTrue(abs(p.posx-expected_posx) <= 0.01 and abs(p.posy-expected_posy) <= 0.01, "The player coordinates should have been closer to expected ones. \nExpected: " + str((expected_posx, expected_posy)) + "\nResult: " + str((p.posx, p.posy)))

    def test_simplistic_move_with_speed_check2(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy, move_angle = row*const.CELL_SIZE, col*const.CELL_SIZE, 0.0, 1.0, 0
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.9*const.CELL_SIZE
        p.max_speedy = 0.9*const.CELL_SIZE
        expected_posx, expected_posy = posx, posy + speedy * p.max_speedy
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        self.assertTrue(abs(p.posx-expected_posx) <= 0.01 and abs(p.posy-expected_posy) <= 0.01, "The player coordinates should have been closer to expected ones. \nExpected: " + str((expected_posx, expected_posy)) + "\nResult: " + str((p.posx, p.posy)))

    def test_simplistic_move_with_speed_check3(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy, move_angle = row*const.CELL_SIZE, col*const.CELL_SIZE, 1.0, 1.0, 270
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.9*const.CELL_SIZE
        p.max_speedy = 0.9*const.CELL_SIZE
        expected_posx, expected_posy = posx + speedx * p.max_speedx, posy
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        self.assertTrue(abs(p.posx-expected_posx) <= 0.01 and abs(p.posy-expected_posy) <= 0.01, "The player coordinates should have been closer to expected ones. \nExpected: " + str((expected_posx, expected_posy)) + "\nResult: " + str((p.posx, p.posy)))

    def test_simplistic_step_with_occlusion(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy, move_angle = row * const.CELL_SIZE, col * const.CELL_SIZE, 1.0, 1.0, 270
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.9*const.CELL_SIZE
        p.max_speedy = 0.9*const.CELL_SIZE
        expected_posx, expected_posy = posx + speedx * p.max_speedx, posy
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        ge.step()
        n = len(p.sight_vertices)
        self.assertTrue(16 >= n, "The player's sight should have been consituted of more vertices than " + str(n))

    def test_empirical_occlusion(self):
        from shapely.occlusion import occlusion
        mpos_x, mpos_y = 0, 0
        sight_triangle_width, sight_triangle_height = 100, 100
        sight_polygon_coords = [[mpos_x, mpos_y], [mpos_x - sight_triangle_width/2, mpos_y + sight_triangle_height], [mpos_x + sight_triangle_width/2, mpos_y + sight_triangle_height]]
        res1, _useless = occlusion(0, 0, sight_polygon_coords, [0, 10, 0, 18, 8, 18, 8, 10], 8)
        res2, _useless = occlusion(0, 0, sight_polygon_coords, [], 0)
        res3, _useless = occlusion(0, 0, sight_polygon_coords, [12, 0, 12, 8, 20, 8, 20, 0], 8)
        self.assertTrue(res1 != res2 and res1 != res3 and res2 == res3, "Those three executions of occlusion() should have returned different results for res1 and res2 but same for res2 and res3")

    def test_simplistic_move_with_collision(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy= row*const.CELL_SIZE, col*const.CELL_SIZE, 1.0, 1.0
        move_angle = 270
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.9*const.CELL_SIZE
        p.max_speedy = 0.9*const.CELL_SIZE
        wall_x_pos = 5 * const.CELL_SIZE
        n_turns = 10
        expected_posx, expected_posy = wall_x_pos-1, posy 
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        for x in xrange(1,n_turns): # Run n_turns turns, so that the player tries to go through the wall
            ge.step()
        self.assertTrue(abs(p.posx-expected_posx) <= 0.01 and abs(p.posy-expected_posy) <= 0.01, 
            "The player coordinates should have been closer to expected ones. \nExpected: " 
            + str((expected_posx, expected_posy)) 
            + "\nResult: " + str((p.posx, p.posy))
        )

    def test_simplistic_move_map_bound_y(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        row, col = 0, 0
        posx, posy, speedx, speedy = row*const.CELL_SIZE, col*const.CELL_SIZE, 1.0, 1.0
        move_angle = 0
        players = self.__setup_players(ge, [(col, row)])
        p = players[0]
        pid = players[0].player_id
        p.max_speedx = 0.5*const.CELL_SIZE
        p.max_speedy = 0.5*const.CELL_SIZE
        expected_posx, expected_posy = posx, ge.slmap.height * const.CELL_SIZE - 1
        ge.set_movement_angle(pid, move_angle)
        ge.set_movement_speedx(pid, speedx)
        ge.set_movement_speedy(pid, speedy)
        for x in xrange(1,30): # Run 30 turns, so that the player tries to go through the wall
            ge.step()
        self.assertTrue(abs(p.posx-expected_posx) <= 0.01 and abs(p.posy-expected_posy) <= 0.01, 
            "The player coordinates should have been closer to expected ones. \nExpected: " 
            + str((expected_posx, expected_posy)) 
            + "\nResult: " + str((p.posx, p.posy))
        )

    def test_visible_players_see_noone(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 4), (4, 7)])
        move_angle = 270 # "->
        ge.set_movement_angle(p1.player_id, move_angle)
        ge.step()
        self.assertTrue(len(p1.visible_players) == 0,
            "The player " + str(p1) + " should see noone. But it is seeing: " + str(p1.visible_players)
        )

    def test_visible_players_see_someone(self):
        self.map_file = "map_test_scinded.hfm"
        ge = self.getGE()
        p1, p2 = self.__setup_players(ge, [(2, 4), (2, 7)])
        move_angle = 270 # "->
        ge.set_movement_angle(p1.player_id, move_angle)
        ge.step()
        self.assertTrue(len(p1.visible_players) == 1,
            "The player (" + str(p1) + ") should see someone. But it is seeing: " + str(p1.visible_players)
        )


if __name__ == '__main__':
    unittest.main()