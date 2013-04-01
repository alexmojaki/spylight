#!/usr/bin/env python

import sys
import unittest
sys.path.append("../")
from server.game_engine import Player

from server.game_engine import GameEngine

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
	
	def test_shoot(self):
		ge = self.getGE()
		players = self.__gp(ge, "__players")
		p1, p2 = Player(0, 0), Player(1, 1)
		p1.posx = 0
		p1.posy = 0
		p2.posx = 10
		p2.posy = 10
		players[0] = p1
		players[1] = p2


if __name__ == '__main__':
	unittest.main()