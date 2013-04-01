#!/usr/bin/env python

import sys
import unittest
sys.path.append("../")

from server.game_engine import GameEngine

class GameEngineTest(unittest.TestCase):
	"""Tests for GameEngine class"""
	def setUp(self):
		self.conf_file = "conf_test.ini"
		self.map_file = "map_test.hfm"

	def getGE(self):
		return GameEngine().init(self.conf_file, self.map_file)
		
	def test_instanciate(self):
		self.getGE()

	def test_load_config_1(self):
		ge = self.getGE()
		self.assertTrue(ge.config is not None, "The config of the GameEngine was not loaded successfully and is None")

	def test_load_config(self):
		ge = self.getGE()
		self.assertTrue(ge.config.send_state_interval == 0.02)

if __name__ == '__main__':
	unittest.main()